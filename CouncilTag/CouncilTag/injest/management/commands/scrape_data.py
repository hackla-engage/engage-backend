from django.core.management.base import BaseCommand, CommandError
from CouncilTag.injest.models import Committee, Agenda, AgendaItem, AgendaRecommendation
from CouncilTag.injest.data import get_data
from django.core.exceptions import *
class Command(BaseCommand):
    help = 'Scrapes the Santa Monica website for meeting information'

    def save_agendaitem(agenda_item):
        new_agenda_item = AgendaItem()
        new_agenda_item.department = agenda_item['Department']
        new_agenda_item.title = agenda_item['title']
        new_agenda_item.sponsors = agenda_item['Sponsors']
        if 'body' in agenda_item:
            new_agenda_item.supplemental = agenda_item['body']['other']
            new_agenda_item.summary = agenda_item['body']['summary']
            if 'background' in agenda_item['body']:
                new_agenda_item.background = agenda_item['body']['background']
        new_agenda_item.save()
        if 'recommendations' in agenda_item:
            new_rec = AgendaRecommendation(recommendations=agenda_item['recommendations'])
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
                ag_item = self.save_agendaitem(ag)
                ag_item.agenda = new_agenda
                r =ag_item.save()
                print(r)
            new_agenda.save()