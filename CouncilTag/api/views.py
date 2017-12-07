from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from CouncilTag.ingest.models import Agenda, Tag, AgendaItem
from CouncilTag.api.serializers import AgendaSerializer, TagSerializer, AgendaItemSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import jwt, json
from CouncilTag import settings
from rest_framework.renderers import JSONRenderer


@api_view(['GET'])
def list_agendas(request, format=None):
    '''
    dfsfs22333
    '''
    agendas = Agenda.objects.all()
    serializer = AgendaSerializer(agendas, many=True)
    return Response(serializer.data)


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
    Login a current user. Expects a username and password
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


@api_view(['GET'])
def get_agendaitem_by_tag(request, tag_name):
    agenda_items = AgendaItem.objects.filter(tags__name = tag_name)
    serialized_items = AgendaItemSerializer(agenda_items, many=True)
    data = {}
    data['tag'] = tag_name
    data['items'] = serialized_items.data
    return Response(data=data)