from django.core.management.base import BaseCommand, CommandError
from CouncilTag.ingest.models import Tag

seed_tags = [
    ("Community", "fa-users"),
    ("Learning", "fa-graduation-cap"),
    ("Health", "fa-stethoscope"),
    ("Economic Opportunity", "fa-chart-line" ),
    ("Responsive Government", "fa-gavel"),
    ("Environment", "fa-tree"),
    ("Sustainability", "fa-recylce"),
    ("Public Safety", "fa-balance-scale"),
    ("Parks and Recreation", "fa-volleyball-ball"),
    ("Free Speech", "fa-comments" ),
    ("Housing", "fa-home"),
    ("Mobility", "fa-accessible-icon" ),
    ("Pets", "fa-paw"),
    ("Zoning", "fa-building"),
    ("Infrastructure", "fa-road"),
    ("Sanitation", "fa-trash"),
]
class Command(BaseCommand):
    help = 'Populates the seed tags that project will start off with'

    def handle(self, *args, **kwargs):
        for tag in seed_tags:
            print("Creating tag entry for {}".format(tag[0]))
            desc = "lorem ipsum dolor dfsadnonsf asf asdf sdaof asdofas dfoas dfosad fadsfdsadsalksjl..."
            if Tag.objects.filter(name=tag[0]).count() == 0:
                Tag(name=tag[0], description=desc, icon=tag[1]).save()
            else:
                t = Tag.objects.filter(name=tag[0]).first()
                t.description = desc
                t.icon = tag[1]
                t.save()
                
