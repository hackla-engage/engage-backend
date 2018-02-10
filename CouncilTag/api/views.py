from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from CouncilTag.ingest.models import Agenda, Tag, AgendaItem, EngageUser
from CouncilTag.api.serializers import AgendaSerializer, TagSerializer, AgendaItemSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import jwt, json
from CouncilTag import settings
from rest_framework.renderers import JSONRenderer


@api_view(['GET'])
def list_agendas(request, format=None):
    '''
    List all of the agends stored in the database
    '''
    agendas = Agenda.objects.all()
    serializer = AgendaSerializer(agendas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def list_agenda_items(request, format=None):
  '''
  List the agendas stored in the database ordered by date only
  for the user's preferred tags
  '''
  print("here in list agenda items")
  print(request.user.tags)
  # request.body.preferences as in docstring
  # agenda_items = AgendaItem.objects.filter(tags__in=json_of_body["preferences"]).distinct()
  # agenda_items_serializer = AgendaItemSerializer(agenda_items, many=True)
  # return Response(agenda_items_serializer.data)
  return Response()
    

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
    '''
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        token = jwt.encode({'user':user.username}, settings.SECRET_KEY)
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
    user = EngageUser.objects.create_user(username, email, password)
    token = jwt.encode({"user":user.username}, settings.SECRET_KEY) 
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
    return Response(status=200)