from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from CouncilTag.injest.models import Agenda
from CouncilTag.api.serializers import AgendaSerializer

@api_view(['GET'])
def list_agendas(request, format=None):
    '''
    dfsfs22333
    '''
    agendas = Agenda.objects.all()
    serializer = AgendaSerializer(agendas, many=True)
    return Response(serializer.data)

# Create your views here.
