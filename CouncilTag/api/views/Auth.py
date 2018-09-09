from rest_framework.response import Response
from CouncilTag.ingest.models import EngageUserProfile, Message, Committee
from CouncilTag.api.serializers import LoginSerializer, SignupSerializer
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from CouncilTag.api.utils import verify_recaptcha, send_mail, isCommentAllowed
from django.contrib.auth.models import AnonymousUser
from CouncilTag import settings
from datetime import datetime
import jwt
import sys
import uuid
import urllib
import random
import bcrypt 
# Special for special user type
from django.contrib.auth import get_user_model
User = get_user_model()

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
