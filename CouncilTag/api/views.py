from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User, AnonymousUser
from CouncilTag.ingest.models import Agenda, Tag, AgendaItem, EngageUserProfile
from CouncilTag.api.serializers import AgendaSerializer, TagSerializer, AgendaItemSerializer
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import jwt, json
from CouncilTag import settings
from rest_framework.renderers import JSONRenderer
from psycopg2.extras import NumericRange

@api_view(['GET'])
def list_agendas(request, format=None):
    '''
    List all of the agends stored in the database
    '''
    agendas = Agenda.objects.all()
    serializer = AgendaSerializer(agendas, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def list_agenda_items(request, format=None):
  '''
  List the agendas stored in the database with different results for logged in users
  or users who are just using the app without logging in.
  For logged in users:
    we get their stored preferred tags from their profile
    return only tags that are contained in a list of the names of those tags
    and we only return the ones 
  For not logged in users:
    we get the most recent agenda items and return those 
  '''
  # Is there no test for figuring if req.user is of AnonymousUser type?
  print(type(request.user))
  if (not isinstance(request.user, AnonymousUser)):
    profile = EngageUserProfile.objects.get(user=request.user)
    tags_query_set = profile.tags.all()
    tags_serialized = TagSerializer(tags_query_set, many=True)
    # tag_names is a list of strings
    tag_names = array_of_ordereddict_to_list_of_names(tags_serialized.data)
    agenda_items = AgendaItem.objects.filter(tags__name__in=tag_names).filter(agenda__meeting_time__contained_by=NumericRange(request._data['begin'], request._data['end']))
    serialized_items = AgendaItemSerializer(agenda_items, many=True)
    data = {}
    data['tags'] = tag_names
    data['items'] = serialized_items.data      
  else:
    print("here")
    agenda_items = AgendaItem.objects.all()
    serialized_items = AgendaItemSerializer(agenda_items, many=True)
    data = {}
    data['tags'] = "all"
    data['items'] = serialized_items.data   
  return Response(data=data)
    

@api_view(['GET'])
def list_tags(request, format=None):
    '''
    List all availabe tags in the project
    '''
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def login_user(request, format=None):
    '''
    Login a current user. Expects an email address and password
    email because we have loaded 'CouncilTag.api.backends.EmailPasswordBackend'
    This basically sets the USERNAME_FIELD = email in the User o
    '''
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(username=email, password=password)
    if user is not None:
        login(request, user) # This is where attributes to the request are stored
        token = jwt.encode({'email':user.email}, settings.SECRET_KEY)
        return Response({'token':token}, status=201)
    else:
        return Response(status=404, data={"error":"wrong username and password"})


@api_view(['POST'])
def signup_user(request, format=None):
    '''
    Signup a new user. Expects a email address and a password.
    '''
    email = request.POST['email']
    password = request.POST['password']
    username = request.POST['name']
    user = User.objects.create_user(username, email, password)
    EngageUserProfile.objects.create(user=user) # Don't need to save any values from it
    token = jwt.encode({"username":user.email}, settings.SECRET_KEY) 
    return Response({"token": token}, status=201)


@api_view(['GET'])
def get_agendaitem_by_tag(request, tag_name):
    agenda_items = AgendaItem.objects.filter(tags__name = tag_name)
    serialized_items = AgendaItemSerializer(agenda_items, many=True)
    data = {}
    data['tag'] = tag_name
    data['items'] = serialized_items.data
    return Response(data=data)

@login_required
@api_view(['POST'])
def add_tag_to_user(request, format=None):
    '''
    /user/add/tag/ JSON body attribute should have an array of tags
    to add to an EngageUserProfile (an array of 1 at least). The user must
    be logged in for this.
    '''
    if len(request._data["tags"]) == 0:
      return Response({"error": "tags were not included"}, status=400)
    profile = EngageUserProfile.objects.get(user=request.user)
    for tag in request._data["tags"]:
      try:
        tag_to_add = Tag.objects.filter(name__contains=tag).first()
        profile.tags.add(tag_to_add)
      except:
        print("Could not add tag (" + tag + ") to user ("+request.user.username+") since it doesn't exist in the ingest_tag table.")
    try:
      profile.save()
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
    if len(request._data["tags"]) == 0:
      return Response({"error": "tags were not included"}, status=400)
    profile = EngageUserProfile.objects.get(user=request.user)
    for tag in request._data["tags"]:
      tag_to_remove = Tag.objects.filter(name__contains=tag).first()
      profile.tags.remove(tag_to_remove)
    try:
      profile.save()
    except:
      return Response(status=500)
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