
from rest_framework.response import Response
from engage.api.serializers import AgendaItemSerializer
from engage.ingest.models import AgendaItem
from django.contrib.auth.decorators import login_required
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_agenda_item(request, agenda_item_id):
    '''
    Returns JSON serialized agenda item
    '''
    agenda_item = AgendaItem.objects.get(agenda_item_id=agenda_item_id)
    if agenda_item is None:
        return Response(data={"error": "No agenda item with id:" + str(agenda_item_id)}, status=404)
    data = AgendaItemSerializer(agenda_item, many=False).data
    return Response(data=data, status=200)


@api_view(['GET'])
def get_agenda_item_detail(request, agenda_item_id):
    '''
    Returns a detail object for an agenda item, including agree/disagree/no_position tallies
    '''
    agenda_item = AgendaItem.objects.get(agenda_item_id=agenda_item_id)
    if agenda_item is None:
        return Response(data={"error": "No agenda item with id:" + str(agenda_item_id)}, status=404)
    messages = Message.objects.filter(agenda_item=agenda_item)
    tallyDict = calculateTallies(messages)
    return Response(data=tallyDict, status=200)

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

