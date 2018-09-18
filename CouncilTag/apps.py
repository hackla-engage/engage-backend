from django.apps import AppConfig
import json
import logging
from CouncilTag.settings import TEST
log = logging.Logger(__name__)

class CouncilTagConfig(AppConfig):
    name = 'CouncilTag'
    def ready(self):
        if not TEST:
            from CouncilTag.ingest.models import Agenda, Committee
            from CouncilTag.api.utils import getLocationBasedDate
            from celery.schedules import crontab
            from CouncilTag.celery import schedule_process_pdf, app
            log.info("SETTING UP CELERY ASYNC TASKS!")
            app.conf.beat_schedule = {}
            app.conf.timezone='UTC'
            committees = Committee.objects.all()
            for committee in committees:
                agendas = Agenda.objects.filter(
                    committee=committee, processed=False)
                for agenda in agendas:
                    agenda.processed = True
                    agenda.save()
                    dt = getLocationBasedDate(agenda.meeting_time, committee.cutoff_offset_days,
                                            committee.cutoff_hour, committee.cutoff_minute, committee.location_tz)
                    log.error(f"scheduling pdf processing for: {dt}")
                    schedule_process_pdf.apply_async(
                        (committee.name, agenda.meeting_id), eta=dt)
                app.conf.beat_schedule[committee.name] = {
                    'task': 'CouncilTag.celery.schedule_committee_processing',
                    'schedule': crontab(hour='*/2', minute='35'),
                    'args': (committee.name,)
                }