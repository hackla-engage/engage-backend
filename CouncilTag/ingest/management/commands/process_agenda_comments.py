from django.core.management.base import BaseCommand, CommandError
from CouncilTag.ingest.models import Committee, Agenda, AgendaItem, AgendaRecommendation, Message
from datetime import datetime
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
        now = datetime(2018, 6, 26, 12, 0, 0, 0)  # example
        # Find agenda between now and +10 hours
        now_plus_tenh = datetime(now.year, now.month, now.day,
                                 now.hour + 10, now.minute, now.second, now.microsecond)
        now_time_stamp = int(now.timestamp())
        now_plus_tenh_time_stamp = int(now_plus_tenh.timestamp())
        upcoming_agendas = Agenda.objects.filter(meeting_time__contained_by=NumericRange(
            now_time_stamp, now_plus_tenh_time_stamp))
        if (len(upcoming_agendas) == 0):
            print("No upcoming agenda near: %s" % (now))
            return
        upcoming_agenda = upcoming_agendas[0]
        upcoming_agenda_items = AgendaItem.objects.filter(
            agenda=upcoming_agenda)
        if (len(upcoming_agenda_items) == 0):
            print("No upcoming agenda items on agenda")
            return
        writePdfForAgendaItems(upcoming_agenda_items)
