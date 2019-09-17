from rest_framework.response import Response
from engage.ingest.models import Agenda, AgendaItem, EngageUserProfile, Message, Committee
from engage.api.serializers import AgendaSerializer, AddMessageSerializer
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.decorators import api_view

from engage.api.utils import verify_recaptcha, send_mail, isCommentAllowed
from django.contrib.auth.models import AnonymousUser
from engage import settings
from datetime import datetime
import uuid
import urllib
import bcrypt
import random
import logging
log = logging.Logger(__name__)


'''Email message comments for either registered or non-registered users'''


@api_view(["POST"])
@swagger_auto_schema(request_body=AddMessageSerializer, responses={'404': "Either committee or ", '401': 'Recaptcha v2 was incorrect or', '400': 'Incorrect parameters', '201': 'OK, message added'})
def addMessage(request, format=None):
    log.error(request.data)
    session_key = request.session.get('session_key', None)
    if (session_key is None):
        session_key = str(uuid.uuid1())
        request.session['session_key'] = session_key
        request.session.modified = True
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
    agenda = Agenda.objects.get(pk=agenda_item.agenda_id)
    if agenda_item is None:
        return Response(data={"error": "Could not find agenda item matching:" + message_info['ag_item']}, status=404)
    if not settings.TEST and not isCommentAllowed(agenda.cutoff_time):
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
        if 'first_name' not in message_info or message_info['first_name'] is None or \
            'last_name' not in message_info or message_info['last_name'] is None or \
            'zipcode' not in message_info or message_info['zipcode'] is None or \
            'email' not in message_info or message_info['email'] is None or \
            'home_owner' not in message_info or message_info['home_owner'] is None or \
            'business_owner' not in message_info or message_info['business_owner'] is None or \
            'resident' not in message_info or message_info['resident'] is None or \
            'works' not in message_info or message_info['works'] is None or \
            'school' not in message_info or message_info['school'] is None or \
            'child_school' not in message_info or message_info['child_school'] is None or \
                'token' not in message_info or message_info['token'] is None:
            return Response(status=400, data={"error": "Missing or incorrect body parameters"})
        messages = Message.objects.filter(session_key=session_key)
        authcode = str(uuid.uuid1()).replace(
            "-", "")[rand_begin:rand_begin + CODE_LENGTH].encode('utf-8')
        if not messages:
            verify_token = message_info['token']
            result = verify_recaptcha(verify_token)
            if not result:
                return Response(status=401)
            authcode_hashed = bcrypt.hashpw(
                authcode, bcrypt.gensalt()).decode('utf-8')
        else:
            authcode_hashed = messages[0].authcode
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
        new_message = Message(agenda_item=agenda_item, user=user,
                              first_name=first_name, last_name=last_name,
                              zipcode=zipcode, email=email,
                              committee=committee, content=content, pro=pro, authcode=authcode_hashed,
                              date=now.timestamp(), sent=0, home_owner=home_owner, business_owner=business_owner,
                              resident=resident, works=works, school=school, child_school=child_school, session_key=session_key)
        new_message.save()
        if len(messages) == 0:
            query_parameters = urllib.parse.urlencode({
                "code": authcode,
                "email": email,
                "type": "email",
                "id": str(new_message.id)
            })
            query_string = 'https://sm.engage.town/#/emailConfirmation?' + query_parameters
            content = '<h3>Thanks for voicing your opinion,</h3> Before we process your comments, please click <a href="' + \
                query_string + '">here</a> to authenticate.<br/><br/> Thank you for your interest in your local government!<br/><br/> If you are receiving this in error, please email: <a href="mailto:engage@engage.town">engage@engage.town</a>. '
            if not settings.TEST:
                response = send_mail(
                    {"user": {"email": email}, "subject": "Verify message regarding agenda item: " + agenda_item.agenda_item_id,
                    "content": content})
                if (not response):
                    new_message.delete()
                    return Response(status=500, data={'error': "Something happened sending you your confirmation email, please contact engage@engage.town"})
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
                              resident=resident, works=works, school=school, child_school=child_school, session_key=session_key)
        new_message.save()
    # Default to unsent, will send on weekly basis all sent=0
    return Response(status=201, data={"success": True, "message": "Message added"})
