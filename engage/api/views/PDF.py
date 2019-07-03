from rest_framework.response import Response
from engage.ingest.models import Agenda
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.decorators import api_view
import logging
log = logging.Logger(__name__)

@api_view(["GET"])
def getPDFLocation(request, meeting_id):
    try:
        agenda = Agenda.objects.get(meeting_id=meeting_id)
        if agenda is not None and agenda.processed and agenda.pdf_location:
            return Response(status=200, data={"location": agenda.pdf_location})
        else:
            return Response(status=400, data={"location": None})
    except:
        log.error("Could not get agenda {}".format(meeting_id))
        return Response(status=400, data={"location": None})