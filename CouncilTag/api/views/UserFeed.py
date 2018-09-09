
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from CouncilTag.ingest.models import AgendaItem, EngageUser, Agenda
from CouncilTag.api.serializers import UserFeedSerializer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework.decorators import api_view
from rest_framework import status, generics
from rest_framework.views import APIView

from psycopg2.extras import NumericRange
from datetime import datetime
import calendar
import pytz

class MediumResultsPagination(LimitOffsetPagination):
    default_limit = 10

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
            tag_names = list(map(lambda x: x.name, tags_query_set))
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

