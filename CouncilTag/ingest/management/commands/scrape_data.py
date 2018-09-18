from django.core.management.base import BaseCommand, CommandError
from CouncilTag.ingest.models import Committee, Agenda, AgendaItem, AgendaRecommendation
from CouncilTag.ingest.data import get_data
from datetime import datetime
from CouncilTag.ingest.tagging import RandomTagEngine
from CouncilTag.ingest.utils import processAgendasForYears


class Command(BaseCommand):
    help = 'Scrapes the Santa Monica website for meeting information'

    def add_arguments(self, parser):
        parser.add_argument('--years', nargs='+', type=int)
        parser.add_argument('--committee', type=str)

    def handle(self, *args, **options):
        print(f"Processing agendas for years: {options['years']} for: {options['committee']}")
        processAgendasForYears(options["years"], options["committee"])
