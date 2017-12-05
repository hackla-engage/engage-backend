from django.core.management.base import BaseCommand, CommandError
from CouncilTag.ingest.models import Tag

seed_tags = [
    "Community",
    "Learning",
    "Health",
    "Economic Opportunity",
    "Responsive Government",
    "Environment",
    "Sustainability",
    "Public Safety",
    "Parks and Recreation",
    "Free Speech",
    "Housing",
    "Mobility",
    "Pets",
    "Zoning",
    "Infrastructure",
    "Sanitation"
]
class Command(BaseCommand):
    help = 'Populates the seed tags that project will start off with'

    def handle(self, *args, **kwargs):
        for tag in seed_tags:
            print("Creating tag entry for {}".format(tag))
            Tag(name=tag).save()
