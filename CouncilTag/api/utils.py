from CouncilTag import settings
from sendgrid.helpers.mail import Email, Content, Mail, Attachment
from datetime import datetime, timedelta
import sendgrid
import logging
import requests
import os
import bcrypt
import base64
import pytz
import googlemaps
log = logging.Logger(__name__)


def verify_recaptcha(token):
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                      'secret': os.environ["RECAPTCHAKEY"], 'response': token})
    response = r.json()
    return response['success']

def array_of_ordereddict_to_list_of_names(tags_ordereddict_array):
    """
    Serializers have a funny organization that isn't helpful in making further queries
    Here we take the list of ordered dictionaries (id: x, name: y) and pull out the name only
    and put that in a names list to return
    """
    names = []
    length = len(list(tags_ordereddict_array))
    for i in range(length):
        names.append(tags_ordereddict_array[i]["name"])
    return names

def check_auth_code(plain_code, hashed):
    dec = bcrypt.hashpw(plain_code.encode('utf-8'),
                        hashed.encode('utf-8')).decode('utf-8')
    if dec == hashed:
        return True
    return False


def calculateTallies(messages_qs):
    pro = 0
    con = 0
    more_info = 0
    home_owner = 0
    business_owner = 0
    resident = 0
    works = 0
    school = 0
    child_school = 0
    total = 0
    for message in messages_qs:
        if message.authcode != None:
            continue
        if message.pro == 0:
            con += 1
        elif message.pro == 1:
            pro += 1
        else:
            more_info += 1
        if message.home_owner:
            home_owner += 1
        if message.business_owner:
            business_owner += 1
        if message.resident:
            resident += 1
        if message.works:
            works += 1
        if message.school:
            school += 1
        if message.child_school:
            child_school += 1
        total += 1
    return {"home_owner": home_owner, "business_owner": business_owner,
            "resident": resident, "works": works, "school": school,
            "child_school": child_school, "pro": pro, "con": con, "more_info": more_info, "total": total}


def getLocationBasedDate(timestamp, cutoff_days_offset, cutoff_hour, cutoff_minute, location_tz):
    """
    @timestamp a UTC timestamp
    @cutoff_dats_offset +/- integer days from now that should be checking date
    @cutoff_hours integer hours for location that should be set
    @cutoff_minutes integer minutes for locaiton that should be set
    @location_tz string timezone for location where meeting takes place
    """
    tz = pytz.timezone(location_tz)
    dt = datetime.utcfromtimestamp(timestamp)
    dt = dt.astimezone(tz)
    if cutoff_days_offset is not None:
        dt = dt + timedelta(days=cutoff_days_offset)
    if cutoff_hour is not None:
        dt = dt.replace(hour=cutoff_hour, minute=cutoff_minute)
    return dt

def isCommentAllowed(timestamp, cutoff_days_offset, cutoff_hours, cutoff_minutes, location_tz):
    dt = getLocationBasedDate(timestamp, cutoff_days_offset, cutoff_hours, cutoff_minutes, location_tz)
    now = datetime.now().astimezone(tz=pytz.timezone(location_tz))
    if (now > dt):
        return False
    return True


def send_mail(mail_message):
    APIKEY = os.environ["SENDGRIDKEY"]
    sg = sendgrid.SendGridAPIClient(apikey=APIKEY)
    from_email = Email("do-not-reply@engage.town")
    if type(mail_message["user"]) is dict:
        to_email = Email(mail_message["user"]["email"])
    else:
        to_email = Email(mail_message["user"].email)
    subject = mail_message["subject"]
    content = Content('text/html', (mail_message["content"]))
    mail = Mail(from_email=from_email, subject=subject,
                to_email=to_email, content=content)

    if "attachment_file_path" in mail_message:
        with open(mail_message["attachment_file_path"], 'rb') as f:
            data = f.read()
            f.close()

        encode = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.content = encode
        attachment.type = mail_message["attachment_type"]
        attachment.filename = mail_message["attachment_file_name"]
        attachment.disposition = "attachment"
        mail.add_attachment(attachment)

    response = sg.client.mail.send.post(request_body=mail.get())
    if response.status_code == 200 or response.status_code == 202:
        return True
    else:
        log.error("Could not send an email from {} to {} about {}".format(from_email,
                                                                          to_email, subject))
        log.error(response.body)
        log.error(response.status_code)
        return False


def send_message(message_record):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    from_email = Email(message_record.user.email)
    to_email = Email(settings.COUNCIL_CLERK_EMAIL)
    subject = "Comment on {}".format(message_record.agenda_item.title)
    content = Content('text/html', message_record.content)
    mail = Mail(from_email=from_email, subject=subject,
                to_email=to_email, content=content)
    response = sg.client.mail.send.post(request_body=mail.get())
    if response.status_code == 200 or response.status_code == 202:
        return True
    else:
        log.error("Could not send an email from {} to {} about {}".format(from_email,
                                                                          to_email, subject))
        log.error(response.body)
        log.error(response.status_code)
        return False
