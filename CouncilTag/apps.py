import os
from django.apps import AppConfig
import json
import logging
from CouncilTag.settings import TEST
import pytz
from datetime import datetime, timedelta
import redis
r = redis.StrictRedis(host=os.environ.get("REDIS_HOST"), port=6379, db=1)

log = logging.Logger(__name__)

class CouncilTagConfig(AppConfig):
    name = 'CouncilTag'
    def ready(self):
        if not TEST:
            from CouncilTag.ingest.models import Agenda, Committee
            from CouncilTag.api.utils import getLocationBasedDate
            from celery.schedules import crontab
            from CouncilTag.celery import schedule_process_pdf, app
            from celery.task.control import inspect
            log.error("SETTING UP CELERY ASYNC TASKS!")
            i = inspect()
            log.error(i.scheduled())
            app.conf.beat_schedule = {}
            app.conf.timezone='UTC'
            committees = Committee.objects.all()
            for committee in committees:
                agendas = Agenda.objects.filter(
                    committee=committee, processed=False)
                for agenda in agendas:
                    dt = getLocationBasedDate(agenda.meeting_time, committee.cutoff_offset_days,
                                            committee.cutoff_hour, committee.cutoff_minute, committee.location_tz)
                    dt = dt + timedelta(minutes=5)
                    log.error(f"scheduling pdf processing for: {dt} for: {committee.name}")
                    dt_utc = datetime.fromtimestamp(dt.timestamp(), tz=pytz.timezone('UTC'))
                    exists = r.get(f"{committee.name}-{agenda.meeting_time}")
                    log.error(exists)
                    if exists is None:
                        r.set(f"{committee.name}-{agenda.meeting_time}", True, ex=3*60)
                        schedule_process_pdf.apply_async(
                            (committee.name, agenda.meeting_id), eta=dt_utc)
                        log.error(f"scheduled pdf processing")
                    else:
                        log.error(f'{committee.name} {agenda.meeting_id} already queued for pdf')
                app.conf.beat_schedule[committee.name] = {
                    'task': 'CouncilTag.celery.schedule_committee_processing',
                    'schedule': crontab(hour='*/2', minute='35'),
                    'args': (committee.name,)
                }
            log.error(i.scheduled())