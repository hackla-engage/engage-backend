from django.apps import AppConfig
import json


class CouncilTagConfig(AppConfig):
    name = 'CouncilTag'

    def ready(self):
        if (!CouncilTag.settings.DEBUG):
            from CouncilTag.ingest.models import Agenda, Committee
            from CouncilTag.api.utils import getLocationBasedDate
            from CouncilTag.celery import schedule_process_pdf
            print("SETTING UP CELERY ASYNC TASKS!")
            committees = Committee.objects.all()
            for committee in committees:
                agendas = Agenda.objects.filter(
                    committee=committee, processed=False)
                for agenda in agendas:
                    dt = getLocationBasedDate(agenda.meeting_time, committee.cutoff_offset_days,
                                            committee.cutoff_hour, committee.cutoff_minute, committee.location_tz)
                    schedule_process_pdf.apply_async(
                        (committee.name, agenda.meeting_id), eta=dt)
