import os
from celery import Celery, task
from celery.schedules import crontab
from datetime import datetime
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CouncilTag.settings')

app = Celery('CouncilTag')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
app.conf.timezone = 'UTC'


@app.on_after_configure.connect
def setup_beats(sender, **kwargs):
    from CouncilTag.ingest.models import Committee
    print("SETTING UP BEATS!")
    committees = Committee.objects.all()
    for committee in committees:
        sender.add_periodic_task(
            crontab(minute=0, hour=0),
            schedule_committee_processing.s(committee.name),
            name=committee.name,
        )

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task
def schedule_process_pdf(committee_name, agenda_id):
    print(
        f"Executing PDF process for {committee_name} and meeting: {agenda_id}")
    from CouncilTag.ingest.models import AgendaItem, Agenda, Committee
    from CouncilTag.ingest.writePdf import writePdfForAgendaItems
    agenda = Agenda.objects.get(meeting_id=agenda_id)
    committee = Committee.objects.get(name=committee_name)
    upcoming_agenda_items = AgendaItem.objects.filter(agenda=agenda)
    if len(upcoming_agenda_items) == 0:
        return
    writePdfForAgendaItems(upcoming_agenda_items, committee, agenda)
    return


@app.task
def schedule_committee_processing(committee_name, **args):
    print("XXXX", committee_name, args)
    from CouncilTag.ingest.utils import processAgendasForYears
    year = datetime.now().year
    processAgendasForYears([year], committee_name)
