from django.core.management.base import BaseCommand, CommandError
from CouncilTag.ingest.models import Committee, Agenda, AgendaItem, AgendaRecommendation, Message
from datetime import datetime, timedelta
from django.core.exceptions import *
from psycopg2.extras import NumericRange
from CouncilTag.ingest.writePdf import writePdfForAgendaItems
from CouncilTag.api.utils import getLocationBasedDate


class Command(BaseCommand):
    help = '''
        Processes the current agendas comments and
        create a PDF and sends it to the appropriate
        council email address. Run every day at noon by cron.
        '''

    def handle(self, *args, **options):
        now = datetime.now()
        # Find agenda between today and next 10 days.
        now_time_stamp = int(now.timestamp())
        committees = Committee.objects.all()
        if len(committees) == 0:
            print(f"No committees to check agendas for")
            return
        for committee in committees:
            print(committee.name)
            cutoff_offset_days = committee.cutoff_offset_days
            cutoff_hour = committee.cutoff_hour
            cutoff_minute = committee.cutoff_minute
            lat = committee.location_lat
            lng = committee.location_lng
            time_delta = 1200  # 1200 seconds, 20m * 60s/m # 21600 is 6 hours
            upcoming_agendas = Agenda.objects.filter(processed=False)
            if (len(upcoming_agendas) == 0):
                # No agendas
                return 
            for agenda in upcoming_agendas:
                meeting_time = agenda.meeting_time
                cutoff_datetime = getLocationBasedDate(
                    meeting_time, cutoff_offset_days, cutoff_hour, cutoff_minute, lat, lng)
                cutoff_timestamp = int(cutoff_datetime.timestamp())
                if (now_time_stamp - time_delta < cutoff_timestamp < now_time_stamp + time_delta):
                    agenda.processed = True
                    agenda.save()
                    upcoming_agenda_items = AgendaItem.objects.filter(
                        agenda=agenda)
                    if (len(upcoming_agenda_items) == 0):
                        print(
                            "No upcoming agenda items on {meeting_time} for {committee.name}")
                        continue
                    writePdfForAgendaItems(upcoming_agenda_items, committee)
