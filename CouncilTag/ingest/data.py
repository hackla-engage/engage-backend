from bs4 import BeautifulSoup
import requests
import json
import io
import datetime
import pytz
from calendar import timegm
import re

local_tz = pytz.timezone("America/Los_Angeles")
current_year = datetime.date.today().year
city_council_agendas_url = "https://www.smgov.net/departments/clerk/agendas.aspx"

def get_data():
    with requests.Session() as sess:
        r = sess.get(city_council_agendas_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        agendas = dict()
        table = soup.find('table', {'class': 'agendaTable'})
        rows = table.findAll('tr')
        for row in rows:
            cells = row.findChildren('td')
            try:
            	date = agenda_date_to_epoch(cells[0])
            except:
            	date = None
            if date and cells[1].string == "Agenda":
                agenda = sess.get(cells[1].findChildren('a', {'href': True})[0]['href']).text
                if "CONSENT CALENDAR" in agenda:
                    agendas[date] = scrape_agenda(agenda, sess)         
    return agendas

def agenda_date_to_epoch(date_str):
    '''Transforms scraped date to epoch time'''
    naive_dt = datetime.datetime.strptime(
        str(current_year) + " " + date_str.string.strip(), '%Y %B %d %I:%M %p')
    local_dt = local_tz.localize(naive_dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    utc_timetuple = utc_dt.timetuple()
    return timegm(utc_timetuple)

def scrape_agenda(agenda, sess):
    # Searches the entire HTML text for the words since it's not yet parsed into html by BS
    soup_agenda = BeautifulSoup(agenda, 'html.parser')
    tableMeeting = soup_agenda.find('table', {'id': 'MeetingDetail'})
    string_sections = tableMeeting.find_all('strong')
    parent = string_sections[0].find_parent("tr")
    next_siblings = parent.find_next_siblings("tr")
    # staff_reports = {} This and commented code block below can be used to automatically group reports by Category
    staff_reports = []
    reports_holder = []
    
    for sibling in next_siblings:
        if sibling.find('strong'):
            if len(reports_holder) != 0:
                staff_reports.append(reports_holder)
                reports_holder = []
            #     staff_reports[agenda_group] = reports_holder
            #     reports_holder = []
            # agenda_heading = re.match('^(\d+)\..*', sibling.text)
            # if agenda_heading:
            #     agenda_group = agenda_heading.group(1)
        else:
            cells = sibling.find_all('td')
            if len(cells) > 2 and u'Title' in cells[2]['class']:
                staff_report = cells[2].find('a', {'href': True})
                if staff_report is None:
                    continue
                staff_report_href = 'http://santamonicacityca.iqm2.com/Citizens/' + staff_report['href']
                try:
                    staff_report_r = sess.get(staff_report_href)
                    staff_report_html = staff_report_r.text
                    s_r_processed = process_staff_report(staff_report_html)
                    if len(s_r_processed) != 0:
                        reports_holder.append(s_r_processed)
                except Exception as e:
                    #We should create a log file to capture this output rather than just printing...
                    print("coult not get: " + staff_report_href)
                    print(e)
                    exit()

    return staff_reports


def process_staff_report(staff_report_html):
    '''
    staff_report_html is the HTML text
    '''
    staff_report_soup = BeautifulSoup(staff_report_html, 'html.parser')
    title = staff_report_soup.find('div', {'class': 'LegiFileTitle'})
    if title:
        title = title.text.strip()
    else:
        return []
    info = staff_report_soup.find('div', {'class': 'LegiFileInfo'})
    info_dict = dict()
    info_dict['Title'] = title
    if info:
        info_rows = info.div.table.find_all(['tr'])
        for info_row in info_rows:
            info_headers = info_row.find_all('th')
            info_values = info_row.find_all('td')
            for i in enumerate(info_headers):
                info_dict[i[1].strong.string] = info_values[i[0]].string
    discussion = staff_report_soup.find('div', {'id': 'divItemDiscussion'})
    if discussion != None:
        discussion = discussion.text.replace('Recommended Action', '').replace('\xa0', '').strip()
        info_dict['Recommendations'] = discussion
    body = staff_report_soup.find('div', {'id': 'divBody'})
    if body != None:
        body_paragraphs = []
        paragraphs = body.div.div.find_all('p')
        for paragraph in paragraphs:
            cleaned = paragraph.text.replace('\xa0', '').strip()
            if cleaned:
                body_paragraphs.append(cleaned)
        info_dict['Body'] = body_paragraphs
    return info_dict
        