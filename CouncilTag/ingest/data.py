import requests
from bs4 import BeautifulSoup
import unicodedata
import datetime
import pytz
from CouncilTag.ingest.models import AgendaItem
from calendar import timegm

local_tz = pytz.timezone("America/Los_Angeles")
city_council_agendas_url = "https://www.smgov.net/departments/clerk/agendas.aspx"

list_of_sections = [u'SPECIAL AGENDA ITEMS', u'CONSENT CALENDAR', u'STUDY SESSION',
                    u'CONTINUED ITEMS', u'ADMINISTRATIVE PROCEEDINGS', u'ORDINANCES',
                    u'STAFF ADMINISTRATIVE ITEMS', u'PUBLIC HEARINGS']


def agenda_date_to_epoch(date_str, year):
    '''Transforms scraped date to epoch time'''
    naive_dt = datetime.datetime.strptime(
        str(year) + " " + date_str.string.strip(), '%Y %B %d %I:%M %p')
    local_dt = local_tz.localize(naive_dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    utc_timetuple = utc_dt.timetuple()
    return timegm(utc_timetuple)


def parse_query_params(params):
    '''
    Takes the split key value pairs which are made up of ["key=value", "key=value", "key="]
    value may be empty except for MeetingID and ID keys
    Returns a dictionary with two keys "MeetingID" and "ID"
    Values are already split on &
    '''
    query = dict()
    for param in params:
        split_param = param.split("=")
        query[split_param[0]] = split_param[1]
    return query


def process_information_section(body):
    table_body = body.find('table')
    if table_body is not None:
        table_row = table_body.find('tr')
        if table_row is not None:
            td_children = table_row.find_all('td')
            department = td_children[0].get_text().replace('&amp;', 'and')
            sponsors = td_children[1].get_text()
            if sponsors == '':
                sponsors = None
    return department, sponsors


def process_actions_section(body):
    actions = []
    paragraphs = body.find_all('p')
    list_actions = body.find('ol')
    if list_actions is not None:
        # preferred method
        next = list_actions.find('li')
        while next is not None:
            if next.name == 'ol':
                actions[-1] += unicodedata.normalize("NFKD", next.get_text())
            else:
                actions.append(unicodedata.normalize("NFKD", next.get_text()))
            next = next.next_sibling
    else:
        paragraphs = paragraphs[1:]
        for paragraph in paragraphs:
            actions.append(unicodedata.normalize("NFKD", paragraph.get_text()))
    if len(actions) > 0 and actions[0] == 'Staff recommends that the City Council:':
        actions = actions[1:]
    return actions


def process_agenda_item(session, prefix, href):
    agenda_item = dict()
    agenda_item_url = prefix + href
    query = href.split('?')
    query_params = query[1].split("&")
    if query[0] != 'Detail_LegiFile.aspx':
        return
    r = session.get(agenda_item_url)
    agenda_item_soup = BeautifulSoup(r.text, 'html.parser')

    params = parse_query_params(query_params)
    ID = params['ID']
    MeetingID = params['MeetingID']
    Title = agenda_item_soup.find(
        'h1', {'id': 'ContentPlaceholder1_lblLegiFileTitle'})
    if Title is None:
        print("TITLE NONE FOR: ", agenda_item_url)
        Title = "SOME TITLE"
        return None
    else:
        Title = Title.get_text().strip()
    bodies = agenda_item_soup.find_all(
        'div', {'class': 'LegiFileSection'})
    info = agenda_item_soup.find('div', {'class': 'LegiFileInfo'})
    agenda_item['Title'] = Title
    agenda_item['ID'] = ID
    agenda_item['MeetingID'] = MeetingID
    if info is not None:
        info_body = info.find('div', {'class': 'LegiFileSectionContents'})
        Department, Sponsors = process_information_section(info_body)
        agenda_item['Department'] = Department
        agenda_item['Sponsors'] = Sponsors
    recommendations_body = agenda_item_soup.find(
        'div', {'id': 'divItemDiscussion'})
    summary_body = agenda_item_soup.find('div', {'id': 'divBody'})
    if recommendations_body is not None:
        agenda_item['Recommendations'] = process_actions_section(
            recommendations_body)
    else:
        agenda_item['Recommendations'] = []
    agenda_item['Body'] = []
    if summary_body is not None:
        Body = summary_body.find_all('p')
        for body_element in Body:
            text = unicodedata.normalize(
                "NFKD", body_element.get_text()).strip()
            if text != '':
                agenda_item['Body'].append(text)
    return agenda_item


def process_siblings(section_begin, section_end):
    next = section_begin
    as_for_section = []
    while next != section_end:
        links = next.find_all('a')
        for a in links:
            a_parent_prev_sibs = a.find_parent().find_previous_siblings()
            if len(a_parent_prev_sibs) == 2:
                as_for_section.append(a.get('href'))
        next = next.find_next_sibling()
    return as_for_section


def scrape_agenda(agenda, sess):
    soup_agenda = BeautifulSoup(agenda, 'html.parser')
    meeting = soup_agenda.find('table', {'id': 'MeetingDetail'})
    sections = meeting.find_all('td', {'class': 'Title'})
    main_sections = []
    processed_sections = {}
    agenda_items = []
    for section in sections:
        strong = section.find('strong')
        if strong is not None and strong.get_text() in list_of_sections:
            parent_tr = section.find_parent()
            main_sections.append(parent_tr)
    for i in range(len(main_sections) - 1):
        processed_sections[main_sections[i].get_text().split(
            ". ")[1]] = process_siblings(main_sections[i], main_sections[i + 1])
    for key, values in processed_sections.items():
        for value in values:
            if value is None:
                continue
            value_noaddr = value.split("?")[1]
            values_split = value_noaddr.split("&")
            params = parse_query_params(values_split)
            agendaitem = AgendaItem.objects.filter(
                agenda_item_id=params["ID"])
            if len(agendaitem) > 0:
                continue
            agenda_item = process_agenda_item(
                sess, 'http://santamonicacityca.iqm2.com/Citizens/', value)
            if agenda_item is not None:
                agenda_items.append(agenda_item)
    return agenda_items


def get_data(year):
    with requests.Session() as sess:
        rget = sess.get(city_council_agendas_url)
        soupget = BeautifulSoup(rget.text, 'html.parser')
        form = soupget.find('form', {'name': 'aspnetForm'})
        formInputs = form.findChildren('input')
        payload = dict()
        for input in formInputs:
            if input.get('name') in [
                "EktronClientManager",
                "__VIEWSTATE",
                "__VIEWSTATEGENERATOR",
                "__EVENTVALIDATION"
            ]:
                payload[input.get('name')] = input.get('value')
        payload["ctl00$ctl00$bodyContent$mainContent$ddlYears"] = str(year)
        r = sess.post(city_council_agendas_url, data=payload)
        soup = BeautifulSoup(r.text, 'html.parser')
        agendas = dict()
        table = soup.find('table', {'class': 'agendaTable'})
        if table is None:
            return None
        rows = table.findAll('tr')
        for row in rows:
            cells = row.findChildren('td')
            try:
                date = agenda_date_to_epoch(cells[0], year)
            except:
                date = None
            if date and cells[1].string == "Agenda":
                agenda = sess.get(cells[1].findChildren(
                    'a', {'href': True})[0]['href']).text
                if "CONSENT CALENDAR" in agenda:
                    agendas[date] = scrape_agenda(agenda, sess)
    return agendas
