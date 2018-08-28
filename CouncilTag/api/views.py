from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.views import APIView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
User = get_user_model()
from CouncilTag.ingest.models import Agenda, Tag, AgendaItem, EngageUserProfile, Message, Committee, EngageUser
from CouncilTag.api.serializers import AgendaSerializer, TagSerializer, AgendaItemSerializer, UserFeedSerializer, CommitteeSerializer
from CouncilTag.api.serializers import VerifySerializer, SignupSerializer, AddMessageSerializer, LoginSerializer, ModifyTagSerializer
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.utils.decorators import method_decorator
from django.utils.deprecation import MiddlewareMixin
from CouncilTag.api.utils import verify_recaptcha, send_mail, isCommentAllowed
import jwt
import json
import pytz
import calendar
import uuid
import urllib
import random
import bcrypt
import sys
from CouncilTag import settings
from psycopg2.extras import NumericRange
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body


class DisableCSRF(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)


class SmallResultsPagination(LimitOffsetPagination):
    default_limit = 2


class MediumResultsPagination(LimitOffsetPagination):
    default_limit = 10


class AgendaView(generics.ListAPIView):
    queryset = Agenda.objects.all().order_by('-meeting_time')
    serializer_class = AgendaSerializer
    pagination_class = SmallResultsPagination


class TagView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserFeed(generics.ListAPIView):
    '''
    List the agendas stored in the database with different results for logged in users
    or users who are just using the app without logging in.
    Query Parameters: begin -- start of datetime you want to query
                      end -- end of datetime you want to query
    For logged in users:
      we get their stored preferred tags from their profile
      return only tags that are contained in a list of the names of those tags
      and we only return the ones
    For not logged in users:
      we get the most recent agenda items and return those
    '''
    serializer_class = UserFeedSerializer
    pagination_class = MediumResultsPagination

    def get_queryset(self):
        print("get queryset")
        # Is there no test for figuring if req.user is of AnonymousUser type?
        data = []
        now = datetime.now(pytz.UTC)
        unixnow = calendar.timegm(now.utctimetuple())
        if (not isinstance(self.request.user, AnonymousUser)):
            user = EngageUser.objects.get(user=self.request.user)
            # tags_query_set = user.tags.all()
            agenda_items = AgendaItem.objects.filter(tags__name__in=tag_names).filter(
                agenda__meeting_time__contained_by=NumericRange(self.request.data['begin'], self.request.data['end']))
            if agenda_items[0].meeting_time > unixnow:
                meeting_held = False
            else:
                meeting_held = True
        else:
            # return the most recent agenda items for the upcoming meeting,
            # if there is no upcoming meeting, show the last meeting instead
            last_run = Agenda.objects.order_by('-meeting_time')[0]
            if last_run.meeting_time > unixnow:
                meeting_held = False
            else:
                meeting_held = True

            agenda_items = last_run.items.all()

        for ag_item in agenda_items:
            data.append({"item": ag_item, "tag": list(
                ag_item.tags.all()), "meeting_already_held": meeting_held})
        return data


def calculateTallies(messages_qs):
    pro = 0
    con = 0
    more_info = 0
    home_owner = 0
    business_owner = 0
    resident = 0
    works = 0
    school = 0
    child_school = 0
    total = 0
    for message in messages_qs:
        if message.authcode != None:
            continue
        if message.pro == 0:
            con += 1
        elif message.pro == 1:
            pro += 1
        else:
            more_info += 1
        if message.home_owner:
            home_owner += 1
        if message.business_owner:
            business_owner += 1
        if message.resident:
            resident += 1
        if message.works:
            works += 1
        if message.school:
            school += 1
        if message.child_school:
            child_school += 1
        total += 1
    return {"home_owner": home_owner, "business_owner": business_owner,
            "resident": resident, "works": works, "school": school,
            "child_school": child_school, "pro": pro, "con": con, "more_info": more_info, "total": total}


@api_view(['GET'])
def get_agenda(request, meeting_id):
    '''
    Returns specified JSON serialized agenda if it exists
    '''
    agenda = Agenda.objects.get(meeting_id=meeting_id)
    if agenda is None:
        return Response(data={"error": "No agenda item with id:" + str(meeting_id)}, status=404)
    data = AgendaSerializer(agenda, many=False).data
    return Response(data=data, status=200)


@api_view(['GET'])
def get_agenda_item(request, agenda_item_id, tz_offset):
    '''
    Returns JSON serialized agenda item
    '''
    agenda_item = AgendaItem.objects.get(agenda_item_id=agenda_item_id)
    if agenda_item is None:
        return Response(data={"error": "No agenda item with id:" + str(agenda_item_id)}, status=404)
    data = AgendaItemSerializer(agenda_item, many=False).data
    return Response(data=data, status=200)


@api_view(['GET'])
def get_agenda_item_detail(request, agenda_item_id, tz_offset):
    '''
    Returns a detail object for an agenda item, including agree/disagree/no_position tallies
    '''
    agenda_item = AgendaItem.objects.get(agenda_item_id=agenda_item_id)
    if agenda_item is None:
        return Response(data={"error": "No agenda item with id:" + str(agenda_item_id)}, status=404)
    messages = Message.objects.filter(agenda_item=agenda_item)
    tallyDict = calculateTallies(messages)
    return Response(data=tallyDict, status=200)


@swagger_auto_schema(request_body=LoginSerializer, method='post')
@api_view(['POST'])
def login_user(request, format=None):
    '''
    Login a current user. Expects an email address and password
    email because we have loaded 'CouncilTag.api.backends.EmailPasswordBackend'
    accepts raw JSON or form-data encoded
    '''
    data = request.data
    email = data['email']
    password = data['password']
    user = authenticate(username=email, password=password)
    if user is not None:
        # This is where attributes to the request are stored
        login(request, user)
        token = jwt.encode({'email': user.email}, settings.SECRET_KEY)
        return Response({'token': token}, status=201)
    else:
        return Response(status=404, data={"error": "wrong username and password"})


@login_required
@api_view(['POST'])
def change_password(request, format=None):
    data = request.data
    if 'password' not in data or 'new_password' not in data:
        return Response(status=404, data={"error": "Expects password and new_password fields"})
    if request.user.check_password(data['password']):
        # Verified password
        request.user.set_password(data['new_password'])
        try:
            request.user.save()
            send_mail({
                "user": request.user,
                "subject": "Reset password",
                "content": "Someone has reset your password. If this was not you, please contact us at: password@engage.town",
            })
        except:
            return Response({"error": "Could not save password"}, status=404)
    else:
        print("Error, user %s attempted to reset password with incorrect password" % (
            request.user.username))
        return Response({"error": "Incorrect password"})


@login_required
@api_view(['POST'])
def update_profile(request, format=None):
    '''
    Update profile booleans
    '''
    data = request.data
    profile = EngageUserProfile.objects.get(user_id=request.user.id)
    if 'home_owner' in data and data['home_owner']:
        profile.home_owner = True
    elif 'home_owner' in data:
        profile.home_owner = False
    if 'resident' in data and data['resident']:
        profile.resident = True
    elif 'resident' in data:
        profile.resident = False
    if 'business_owner' in data and data['business_owner']:
        profile.business_owner = True
    elif 'business_owner' in data:
        profile.business_owner = False
    if 'works' in data and data['works']:
        profile.works = True
    elif 'works' in data:
        profile.works = False
    if 'school' in data and data['school']:
        profile.school = True
    elif 'school' in data:
        profile.school = False
    if 'child_school' in data and data['child_school']:
        profile.child_school = True
    elif 'child_school' in data:
        profile.child_school = False
    try:
        profile.save()
        return Response(status=200)
    except:
        print("Unexpected error:", sys.exc_info()[0])
    return Response(status=404)


class VerifyView(APIView):
    @swagger_auto_schema(request_body=VerifySerializer)
    def post(self, request):
        """Verify signup for user or email message for non-user"""
        data = request.data
        if 'type' not in data or 'code' not in data or 'email' not in data:
            return Response(data={"error": "Data object must contain code, email, id, and type"}, status=404)
        if data['type'] not in ["email", "signup"]:
            return Response(data={"error": "Data object's type must be signup or email"}, status=404)
        user = User.objects.get(email=data["email"])
        if data['type'] == 'email':
            if 'id' not in data:
                return Response(data={"error": "Data object must contain code, email, id, and type, for email message"}, status=404)
            message = Message.objects.get(id=data['id'])
            if message is None:
                return Response(data={"error": "Message id: " + data['id'] + "was not found"}, status=404)
            authcode = message.authcode
            if authcode is None:
                return Response(data={"error": "Message has already been verified"}, status=200)
            if not check_auth_code(data['code'], authcode):
                return Response(data={"error": "Authcodes do not match for email"}, status=404)
            message.authcode = None
            message.save()
            return Response(status=200, data={"success":True})
        elif data['type'] == 'signup':
            if user is None:
                return Response(data={"error": "User not found"}, status=404)
            profile = EngageUserProfile.objects.get(user=user)
            authcode = profile.authcode
            if authcode is None:
                return Response(data={"error": "User has already been verified"}, status=200)
            if not check_auth_code(data['code'], authcode):
                return Response(data={"error": "Authcodes do not match for email"}, status=404)
            profile.authcode = None
            profile.save()
            return Response(status=200, data={"success": True})
        return Response(status=500)


def check_auth_code(plain_code, hashed):
    dec = bcrypt.hashpw(plain_code.encode('utf-8'),
                        hashed.encode('utf-8')).decode('utf-8')
    if dec == hashed:
        return True
    return False


class SignupView(APIView):
    @swagger_auto_schema(request_body=SignupSerializer)
    def post(self, request):
        '''
        Signup new user. Must be unique username and email. Will create authcode and email to user.
        '''
        data = request.data
        if 'first_name' not in data or 'last_name' not in data or 'username' not in data or 'password' not in data or 'email' not in data:
            return Response(data={"error": "Data object must contain first_name, last_name, username, password, and email"}, status=400)
        email = data['email']
        password = data['password']
        username = data['username']
        first_name = data['first_name']
        last_name = data['last_name']
        CODE_LENGTH = 8
        rand_begin = random.randint(0, 32 - CODE_LENGTH)
        authcode = str(uuid.uuid1()).replace(
            "-", "")[rand_begin:rand_begin + CODE_LENGTH].encode('utf-8')
        authcode_hashed = bcrypt.hashpw(
            authcode, bcrypt.gensalt()).decode('utf-8')

        if 'home_owner' in data and data['home_owner']:
            home_owner = True
        else:
            home_owner = False
        if 'resident' in data and data['resident']:
            resident = True
        else:
            resident = False
        if 'business_owner' in data and data['business_owner']:
            business_owner = True
        else:
            business_owner = False
        if 'works' in data and data['works']:
            works = True
        else:
            works = False
        if 'school' in data and data['school']:
            school = True
        else:
            school = False
        if 'child_school' in data and data['child_school']:
            child_school = True
        else:
            child_school = False
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            # Don't need to save any values from it
            EngageUserProfile.objects.create(
                user=user, home_owner=home_owner, resident=resident, business_owner=business_owner,
                works=works, school=school, child_school=child_school, authcode=authcode_hashed)
            query_parameters = urllib.parse.urlencode({
                "code": authcode,
                "email": email,
                "type": "signup",
                "id": ""
            })
            print("ZXY:", query_parameters)
            query_string = 'https://engage-santa-monica.herokuapp.com/#/emailConfirmation?' + query_parameters
            content = '<html><body><h3>Welcome to the Engage platform for Santa Monica,</h3> Please click <a href="' + \
                query_string + '">here</a> to authenticate.<br/><br/>Thank you for your interest in your local government!<br/><br/> If you are receiving this in error, please email: <a href="mailto:engage@engage.town">engage@engage.town</a>.</body></html>'
            print(content)
            if not settings.DEBUG:
                sent_mail = send_mail(
                    {"user": user, "subject": "Please authenticate your email for the Engage platform",
                     "content": content})
                print("SENT MAIL:", sent_mail)
            token = jwt.encode({"username": user.email}, settings.SECRET_KEY)
            return Response({"token": token}, status=201)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return Response(status=404)


@api_view(['GET'])
def get_agendaitem_by_tag(request, tag_name):
    '''
       Get agenda items for a specific tag name type. 
       Can ammend returns with offset and limit query parameters
    '''
    agenda_items = AgendaItem.objects.filter(
        tags__name=tag_name).select_related().all()
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    total_length = len(agenda_items)
    num_returned = total_length
    if (offset is not None):
        try:
            offset = int(offset)
            end = None
            if (limit is not None):
                limit = int(limit)
                end = limit + offset
            if offset <= len(agenda_items):
                agenda_items = agenda_items[offset: end]
                num_returned = len(agenda_items)
            else:
                return Response(status=400)
        except ValueError:
            return Response(status=400)
    serialized_items = AgendaItemSerializer(agenda_items, many=True)
    data = {}
    data['tag'] = tag_name
    data['items'] = serialized_items.data
    data['limit'] = limit
    data['offset'] = offset
    data['total_items'] = total_length
    data['items_returned'] = num_returned
    return Response(data=data)


class UserTagView(LoginRequiredMixin, APIView):
    @swagger_auto_schema(request_body=no_body, responses={"404": "Not logged in, should be 401", "200": "OK, retrieved tags"})
    def get(self, request):
        user = EngageUserProfile.objects.get(user=request.user)
        tags = user.tags.all()
        tags_list = []
        for tag in tags:
            tags_list.append(tag.name)
        return Response(data=tags_list)

    @swagger_auto_schema(request_body=ModifyTagSerializer, responses={"404": "Not logged in, should be 401", "200": "OK, added tags"})
    def post(self, request):
        '''
        Add new tags (array of tag names) to user's profile
        '''
        if len(request.data["tags"]) == 0:
            return Response({"error": "tags were not included"}, status=400)
        user = EngageUserProfile.objects.get(user=request.user)
        for tag in request.data["tags"]:
            try:
                tag_to_add = Tag.objects.filter(name__contains=tag).first()
                if tag_to_add is not None:
                    user.tags.add(tag_to_add)
            except:
                print("Could not add tag (" + tag + ") to user (" + request.user.username +
                      ") since it doesn't exist in the ingest_tag table.")
        try:
            user.save()
        except:
            return Response(status=500)
        return Response(status=200)

    @swagger_auto_schema(request_body=ModifyTagSerializer, responses={"404": "Not logged in, should be 401", "200": "OK, removed tags"})
    def delete(self, request):
        '''
        Delete array of existing tags from user
        '''
        if len(request.data["tags"]) == 0:
            return Response({"error": "tags were not included"}, status=400)
        user = EngageUserProfile.objects.get(user=request.user)
        for tag in request.data["tags"]:
            tag_to_remove = Tag.objects.filter(name__contains=tag).first()
            if tag_to_remove is not None:
                user.tags.remove(tag_to_remove)
        try:
            user.save()
        except:
            return Response(status=500)
        return Response(status=200)


'''Email message comments for either registered or non-registered users'''


# @csrf_exempt # Complex, if not user, post still needs a CSRF token... which it doesn't have
@api_view(["POST"])
@swagger_auto_schema(request_body=AddMessageSerializer, responses={'404': "Either committee or ", '401': 'Recaptcha v2 was incorrect or', '400': 'Incorrect parameters', '201': 'OK, message added'})
def addMessage(request, format=None):
    '''Add a new message to list to be sent to city council'''
    now = datetime.now()
    message_info = request.data
    if 'ag_item' not in message_info or 'committee' not in message_info or 'content' not in message_info or 'pro' not in message_info:
        return Response(status=400, data={"error": "Missing or incorrect body parameters?"})
    committee = Committee.objects.get(
        name__contains=message_info['committee'])
    if committee is None:
        return Response(data={"error": "Could not find committee matching:" + message_info['committee']}, status=404)
    agenda_item = AgendaItem.objects.get(pk=message_info['ag_item'])
    if agenda_item is None:
        return Response(data={"error": "Could not find agenda item matching:" + message_info['ag_item']}, status=404)
    if not settings.DEBUG and not isCommentAllowed(agenda_item.meeting_time, committee.cutoff_offset_days, committee.cutoff_hour, committee.cutoff_minute):
        return Response(status=401, data={"error": "Could not add comment about agenda item because past the cutoff time"})
    content = message_info['content']
    pro = message_info['pro']
    first_name = None
    last_name = None
    zipcode = 90401
    user = None
    email = None
    user = None
    home_owner = False
    business_owner = False
    resident = False
    works = False
    school = False
    child_school = False
    CODE_LENGTH = 8
    rand_begin = random.randint(0, 32 - CODE_LENGTH)
    authcode_hashed = None
    if (isinstance(request.user, AnonymousUser)):
        if 'token' not in message_info:
            return Response(status=400, data={"error": "Not logged in user must use recaptcha."})
        verify_token = message_info['token']
        result = verify_recaptcha(verify_token)
        if not result:
            return Response(status=401)
        authcode = str(uuid.uuid1()).replace(
            "-", "")[rand_begin:rand_begin + CODE_LENGTH].encode('utf-8')
        authcode_hashed = bcrypt.hashpw(
            authcode, bcrypt.gensalt()).decode('utf-8')
        if 'first_name' not in message_info or message_info['first_name'] is None or \
            'last_name' not in message_info or message_info['last_name'] is None or \
            'zipcode' not in message_info or message_info['zipcode'] is None or \
            'email' not in message_info or message_info['email'] is None or \
            'home_owner' not in message_info or message_info['home_owner'] is None or \
            'business_owner' not in message_info or message_info['business_owner'] is None or \
            'resident' not in message_info or message_info['resident'] is None or \
            'works' not in message_info or message_info['works'] is None or \
            'school' not in message_info or message_info['school'] is None or \
                'child_school' not in message_info or message_info['child_school'] is None:
            return Response(status=400, data={"error": "Missing or incorrect body parameters"})
        first_name = message_info['first_name']
        last_name = message_info['last_name']
        zipcode = message_info['zipcode']
        email = message_info['email']
        home_owner = message_info['home_owner']
        business_owner = message_info['business_owner']
        resident = message_info['resident']
        works = message_info['works']
        school = message_info['school']
        child_school = message_info['child_school']
    else:
        user = request.user
        profile = EngageUserProfile.objects.get(user_id=request.user.id)
        home_owner = profile.home_owner
        business_owner = profile.business_owner
        resident = profile.resident
        works = profile.works
        school = profile.school
        child_school = profile.child_school
        if profile.authcode != None:
            authcode_hashed = profile.authcode
    new_message = Message(agenda_item=agenda_item, user=user,
                          first_name=first_name, last_name=last_name,
                          zipcode=zipcode, email=email,
                          committee=committee, content=content, pro=pro, authcode=authcode_hashed,
                          date=now.timestamp(), sent=0, home_owner=home_owner, business_owner=business_owner,
                          resident=resident, works=works, school=school, child_school=child_school)
    new_message.save()
    if user is None:
        query_parameters = urllib.parse.urlencode({
            "code": authcode,
            "email": email,
            "type": "email",
            "id": str(new_message.id)
        })
        query_string = 'https://engage-santa-monica.herokuapp.com/#/emailConfirmation?' + query_parameters
        content = '<h3>Thanks for voicing your opinion,</h3> Before we process your comment, please click <a href="' + \
            query_string + '">here</a> to authenticate.<br/><br/>If you create and authenticate an account you will never have to authenticate for messages again.<br/><br/> Thank you for your interest in your local government!<br/><br/> If you are receiving this in error, please email: <a href="mailto:engage@engage.town">engage@engage.town</a>. '
        send_mail(
            {"user": {"email": email}, "subject": "Verify message regarding agenda item: " + agenda_item.agenda_item_id,
             "content": content})
    # Default to unsent, will send on weekly basis all sent=0
    return Response(status=201)


def array_of_ordereddict_to_list_of_names(tags_ordereddict_array):
    """
    Serializers have a funny organization that isn't helpful in making further queries
    Here we take the list of ordered dictionaries (id: x, name: y) and pull out the name only
    and put that in a names list to return
    """
    names = []
    length = len(list(tags_ordereddict_array))
    for i in range(length):
        names.append(tags_ordereddict_array[i]["name"])
    return names
