from django.apps import AppConfig
import json
import logging
from CouncilTag.settings import TEST, CELERY, DEBUG, r
import pytz
from datetime import datetime, timedelta

log = logging.Logger(__name__)


class CouncilTagConfig(AppConfig):
    name = 'CouncilTag'

    def ready(self):
        if CELERY:
            from CouncilTag.ingest.models import Agenda, Committee
            from CouncilTag.api.utils import getLocationBasedDate
            from celery.schedules import crontab
            from CouncilTag.celery import schedule_process_pdf, APP
            from celery.task.control import inspect
            log.error("SETTING UP CELERY ASYNC TASKS!")
            i = inspect()
            log.error(i.scheduled())
            APP.conf.beat_schedule = {}
            APP.conf.timezone = 'UTC'
            committees = Committee.objects.all()
            for committee in committees:
                agendas = Agenda.objects.filter(
                    committee=committee, processed=False)
                for agenda in agendas:
                    dt = getLocationBasedDate(agenda.meeting_time, committee.cutoff_offset_days,
                                              committee.cutoff_hour, committee.cutoff_minute, committee.location_tz)
                    dt = dt + timedelta(minutes=5)
                    log.error(
                        f"scheduling pdf processing for: {dt} for: {committee.name}")
                    dt_utc = datetime.fromtimestamp(
                        dt.timestamp(), tz=pytz.timezone('UTC'))
                    exists = r.get(f"{committee.name}-{agenda.meeting_time}")
                    if exists is None:
                        r.set(f"{committee.name}-{agenda.meeting_time}",
                              "true", ex=3 * 60)
                        print("XXXX:", dt_utc, datetime.now(tz=pytz.timezone('UTC')))
                        if dt_utc > datetime.now(tz=pytz.timezone('UTC')):
                            schedule_process_pdf.apply_async(
                                (committee.name, agenda.meeting_id), eta=dt_utc)
                            log.error(f"scheduled pdf processing")
                    else:
                        log.error(
                            f'{committee.name} {agenda.meeting_id} already queued for pdf')
                APP.conf.beat_schedule[committee.name] = {
                    'task': 'CouncilTag.celery.schedule_committee_processing',
                    'schedule': crontab(hour='*', minute='*/30'),
                    'args': (committee.name,)
                }
            log.error(i.scheduled())
