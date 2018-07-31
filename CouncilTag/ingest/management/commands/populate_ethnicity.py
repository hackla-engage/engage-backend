from django.core.management.base import BaseCommand, CommandError
from CouncilTag.ingest.models import Ethnicity

class Command(BaseCommand):

    help = "populates the ethnicity groups to the Ethnicity table"

    def handle(self, *args, **kwargs):
        ethnicity_groups = ["white", "Black or African American","American Indian or Alaska Native", "Asian", "Native Hawaiian or Other Pacific Islander"]

        initial_ethnicity = [eth.name for eth in Ethnicity.objects.all()] 

        for ethnicity in ethnicity_groups:
            print(f"populating ethnicity for {ethnicity}")
            if ethnicity in initial_ethnicity:
                self.stdout("Ethnicity already in table")
            else:
                eth = Ethnicity(name=ethnicity)
                eth.save()
