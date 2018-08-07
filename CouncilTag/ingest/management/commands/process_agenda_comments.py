from django.core.management.base import BaseCommand, CommandError
from CouncilTag.ingest.models import Committee, Agenda, AgendaItem, AgendaRecommendation, Message
from datetime import datetime, timedelta
from django.core.exceptions import *
from psycopg2.extras import NumericRange
from CouncilTag.ingest.writePdf import writePdfForAgendaItems

class Command(BaseCommand):
    help = '''
        Processes the current agendas comments and
        create a PDF and sends it to the appropriate
        council email address. Run every day at noon by cron.
        '''

    def handle(self, *args, **options):
        #now = datetime.utcnow()
        now = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour, datetime.now().minute, datetime.now().second, datetime.now().microsecond)
        # Find agenda between today and next 10 days.
        now_plus_tenh = now + timedelta(days=10) 
        
        now_time_stamp = int(now.timestamp())
        now_plus_tenh_time_stamp = int(now_plus_tenh.timestamp())

        upcoming_agendas = Agenda.objects.filter(meeting_time__contained_by=NumericRange(
            now_time_stamp, now_plus_tenh_time_stamp))

        if (len(upcoming_agendas) == 0):
            print(f"No upcoming agenda between {now.strftime('%m/%d/%Y')} and {now_plus_tenh.strftime('%m/%d/%Y')}")
            return
        upcoming_agenda = upcoming_agendas[0]
        upcoming_agenda_items = AgendaItem.objects.filter(
            agenda=upcoming_agenda)
        if (len(upcoming_agenda_items) == 0):
            print("No upcoming agenda items on agenda")
            return
        writePdfForAgendaItems(upcoming_agenda_items)
