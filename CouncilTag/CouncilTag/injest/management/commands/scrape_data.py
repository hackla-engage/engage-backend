from django.core.management.base import BaseCommand, CommandError
from CouncilTag.injest.models import Committee, Agenda, AgendaItem, AgendaRecommendation
from CouncilTag.injest.data import get_data
from django.core.exceptions import *
class Command(BaseCommand):
    help = 'Scrapes the Santa Monica website for meeting information'

    def save_agendaitem(self, agenda_item, new_agenda):
        new_agenda_item = AgendaItem()
        for g in agenda_item:
            new_agenda_item.department = g['Department']
            new_agenda_item.title = g['title']
            new_agenda_item.sponsors = g['Sponsors']
            if 'body' in agenda_item:
                new_agenda_item.supplemental = g['body']['other']
                new_agenda_item.summary = ['body']['summary']
                if 'background' in g['body']:
                    new_agenda_item.background = g['body']['background']
            new_agenda.save()
            new_agenda_item.agenda = new_agenda
            new_agenda_item.save()
            if 'recommendations' in g:
                new_rec = AgendaRecommendation(recommendation=g['recommendations'])
                new_rec.agenda_item = new_agenda_item
                new_rec.save()
            return agenda_item
            

    def handle(self, *args, **options):
        try:
            committee = Committee.objects.get(name="City Council")
        except ObjectDoesNotExist:
            committee = Committee(name="City Council").save()
        agendas = get_data()
        for meeting_time, agenda in agendas.items():
            new_agenda = Agenda(meeting_time = meeting_time)
            new_agenda.committee = committee
            for ag in agenda:
                
                ag_item = self.save_agendaitem(ag, new_agenda)
                
            new_agenda.save()