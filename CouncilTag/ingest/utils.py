from CouncilTag.ingest.models import Committee, Agenda, AgendaItem, AgendaRecommendation
from CouncilTag.ingest.tagging import RandomTagEngine
from django.core.exceptions import ObjectDoesNotExist
from CouncilTag.ingest.data import get_data
from celery.schedules import crontab
from CouncilTag.celery import schedule_process_pdf, app
from datetime import datetime, timedelta
from CouncilTag.settings import r

def save_agendaitem(agenda_item, new_agenda, meeting_time):
    agendaitem = AgendaItem.objects.filter(
        agenda_item_id=agenda_item['ID'])
    if len(agendaitem) == 0:
        random_tagger = RandomTagEngine()
        new_agenda_item = AgendaItem()
        new_agenda_item.department = agenda_item['Department']
        new_agenda_item.title = agenda_item['Title']
        new_agenda_item.sponsors = agenda_item['Sponsors']
        new_agenda_item.meeting_time = meeting_time
        new_agenda_item.agenda_item_id = agenda_item['ID']
        if 'Body' in agenda_item:
            new_agenda_item.body = agenda_item['Body']
        else:
            new_agenda_item.body = []
        new_agenda.save()
        new_agenda_item.agenda = new_agenda
        new_agenda_item.save()
        tags = random_tagger.find_tags(new_agenda_item)
        random_tagger.apply_tags(new_agenda_item, tags)
        if 'Recommendations' in agenda_item:
            new_rec = AgendaRecommendation(
                recommendation=agenda_item['Recommendations'])
            new_rec.agenda_item = new_agenda_item
            new_rec.save()


def processAgendasForYears(years, committee_name):
    try:
        committee = Committee.objects.get(name=committee_name)
    except ObjectDoesNotExist:
        committee = Committee(name="Santa Monica City Council", email="engage@engage.town",
                              cutoff_offset_days=0, cutoff_hour=11, cutoff_minute=59, location_lat=34.024212, location_lng=-118.496475, location_tz="America/Los_Angeles")
        committee.save()
    for year in years:
        agenda_values = get_data(year=year)
        if agenda_values is None:
            print(f"No agendas/items for {year}")
            continue
        for time, agenda in agenda_values.items():
            if len(agenda) > 0:
                found_agenda = Agenda.objects.filter(
                    meeting_time=time).first()
                print(found_agenda)
                if found_agenda is None:
                    found_agenda = Agenda(meeting_time=time)
                    found_agenda.committee = committee
                    found_agenda.meeting_id = agenda[0]['MeetingID']
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
                        log.error(f'{committee.name} {agenda.meeting_id} already queued for pdf in utils')

                for ag_item in agenda:
                    save_agendaitem(ag_item, found_agenda, time)
                found_agenda.save()
