from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
User = get_user_model()
from CouncilTag.ingest.models import Agenda, Tag, AgendaItem, EngageUserProfile, Message, Committee, EngageUser
from CouncilTag.api.serializers import AgendaSerializer, TagSerializer, AgendaItemSerializer, UserFeedSerializer, CommitteeSerializer
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from datetime import datetime
from CouncilTag.api.utils import verify_recaptcha
import jwt
import json
import pytz
import calendar
from CouncilTag import settings
from rest_framework.renderers import JSONRenderer
from psycopg2.extras import NumericRange


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
            tags_query_set = user.tags.all()
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


@api_view(['POST'])
def signup_user(request, format=None):
    '''
    Signup a new user. Expects a email address and a password.
    now in json body type, anyway it seems POST is deprecated
    also data seems to handle form-data as well as raw json
    '''
    data = request.data
    email = data['email']
    password = data['password']
    username = data['name']
    user = User.objects.create_user(username, email, password)
    # Don't need to save any values from it
    EngageUserProfile.objects.create(user=user)
    token = jwt.encode({"username": user.email}, settings.SECRET_KEY)
    return Response({"token": token}, status=201)


@api_view(['GET'])
def get_agendaitem_by_tag(request, tag_name):
    agenda_items = AgendaItem.objects.filter(
        tags__name=tag_name).select_related().all()
    serialized_items = AgendaItemSerializer(agenda_items, many=True)
    data = {}
    data['tag'] = tag_name
    data['items'] = serialized_items.data
    return Response(data=data)


@login_required
@api_view(['GET'])
def get_user_tags(request, format=None):
    user = EngageUserProfile.objects.get(user=request.user)
    tags = user.tags.all()
    tags_list = []
    for tag in tags:
      tags_list.append(tag.name)
    return Response(data=tags_list)


@login_required
@api_view(['POST'])
def add_tag_to_user(request, format=None):
    '''
    /user/add/tag/ JSON body attribute should have an array of tags
    to add to an EngageUserProfile (an array of 1 at least). The user must
    be logged in for this.
    '''
    if len(request.data["tags"]) == 0:
        return Response({"error": "tags were not included"}, status=400)
    user = EngageUserProfile.objects.get(user=request.user)
    for tag in request.data["tags"]:
        try:
            tag_to_add = Tag.objects.filter(name__contains=tag).first()
            user.tags.add(tag_to_add)
        except:
            print("Could not add tag (" + tag + ") to user (" + request.user.username +
                  ") since it doesn't exist in the ingest_tag table.")
    try:
        user.save()
    except:
        return Response(status=500)
    return Response(status=200)


@login_required
@api_view(['POST'])
def del_tag_from_user(request, format=None):
    '''
    /user/del/tag/ JSON body attribute should have an array of tags
    to delete from an EngageUserProfile (an array of 1 at least). The user must
    be logged in for this.
    '''
    if len(request.data["tags"]) == 0:
        return Response({"error": "tags were not included"}, status=400)
    user = EngageUserProfile.objects.get(user=request.user)
    for tag in request.data["tags"]:
        tag_to_remove = Tag.objects.filter(name__contains=tag).first()
        user.tags.remove(tag_to_remove)
    try:
        user.save()
    except:
        return Response(status=500)
    return Response(status=200)


# @login_required(login_url="/api/login")
@api_view(['POST'])
def add_message(request, format=None):
    '''
    /send/message JSON body
    Required Keys:
    @committee: string committee name, e.g. "Santa Monica City Council", must be same as in agenda item.
    @ag_item: item id, integer
    @content: string, no format required
    @token: token string from Google recaptcha
    @pro: boolean, True == Pro, False == Con
    If not signed in:
    @first: string
    @last: string
    @zip: integer
    @email: string
    '''
    now = datetime.now().timestamp()
    message_info = request.data
    committee = Committee.objects.get(
        name__contains=message_info['committee'])
    agenda_item = AgendaItem.objects.get(pk=message_info['ag_item'])
    content = message_info['content']
    verify_token = message_info['token']
    pro = message_info['pro']
    result = verify_recaptcha(verify_token)
    if not result:
        return Response(status=400)
    first_name = None
    last_name = None
    zipcode = 90401
    user = None
    ethnicity = None
    email = None
    user = None
    if (isinstance(request.user, AnonymousUser)):
        first_name = message_info['first']
        last_name = message_info['last']
        zipcode = message_info['zip']
        email = message_info['email']
    else:
        user = request.user
    new_message = Message(agenda_item=agenda_item, user=user,
                          first_name=first_name, last_name=last_name,
                          zipcode=zipcode, email=email, ethnicity=ethnicity,
                          committee=committee, content=content, pro=pro,
                          date=now, sent=0)
    # Default to unsent, will send on weekly basis all sent=0
    new_message.save()
    return Response(status=200)


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
