import os
import logging
import functools
from datetime import datetime
from celery import Celery
from celery.schedules import crontab

log = logging.Logger(__name__)
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CouncilTag.settings')

APP = Celery('CouncilTag')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
APP.config_from_object('django.conf:settings', namespace="CELERY")

# Load task modules from all registered Django APP configs.
APP.autodiscover_tasks()
APP.conf.timezone = 'UTC'
APP.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': 'redis://localhost:6379/0',
        'default_timeout': 60 * 60
    }
}


@APP.on_after_configure.connect
def setup_beats(sender, **kwargs):
    from CouncilTag.ingest.models import Committee
    log.info("SETTING UP BEATS!")
    committees = Committee.objects.all()
    for committee in committees:
        sender.add_periodic_task(
            crontab(minute=35, hour='*/2'),
            schedule_committee_processing.s(committee.name),
            name=committee.name,
        )


@APP.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@APP.task()
def schedule_process_pdf(committee_name, agenda_id):
    from django.db.models import ObjectDoesNotExist
    log.error(
        f"Executing PDF process for {committee_name} and meeting: {agenda_id}")
    from CouncilTag.ingest.models import AgendaItem, Agenda, Committee
    from CouncilTag.ingest.writePdf import writePdfForAgendaItems
    try:
        agenda = Agenda.objects.get(meeting_id=agenda_id, processed=False)
        agenda.processed = True
        agenda.save()
        committee = Committee.objects.get(name=committee_name)
        upcoming_agenda_items = AgendaItem.objects.filter(agenda=agenda)
        if upcoming_agenda_items is None:
            return
        writePdfForAgendaItems(upcoming_agenda_items, committee, agenda)
    except ObjectDoesNotExist as exc:
        log.error('Attempted to process agenda %s but it failed to find the item that was still unprocessed %s' %(agenda_id, exc))
    return


@APP.task
def schedule_committee_processing(committee_name, **args):
    log.error(f"Executing scraping for {committee_name}")
    from CouncilTag.ingest.utils import processAgendasForYears
    year = datetime.now().year
    processAgendasForYears([year], committee_name)
