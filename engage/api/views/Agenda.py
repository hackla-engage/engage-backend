
from rest_framework.response import Response
from engage.api.serializers import AgendaSerializer
from engage.ingest.models import Agenda
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination


class SmallResultsPagination(LimitOffsetPagination):
    default_limit = 2


class AgendaView(generics.ListAPIView):
    queryset = Agenda.objects.all().order_by('-meeting_time')
    serializer_class = AgendaSerializer
    pagination_class = SmallResultsPagination


@api_view(['GET'])
def get_agenda(request, meeting_id, format=None):
    '''
    Returns specified JSON serialized agenda if it exists
    '''
    agenda = Agenda.objects.get(meeting_id=meeting_id)
    if agenda is None:
        return Response(data={"error": "No agenda item with id:" + str(meeting_id)}, status=404)
    data = AgendaSerializer(agenda, many=False).data
    return Response(data=data, status=200)
