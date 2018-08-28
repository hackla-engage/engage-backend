import sendgrid
import logging
import requests
import os
from CouncilTag import settings
from sendgrid.helpers.mail import Email, Content, Mail, Attachment
import base64
import pytz
from datetime import datetime, timedelta
import googlemaps
log = logging.Logger(__name__)


def verify_recaptcha(token):
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                      'secret': os.environ["RECAPTCHAKEY"], 'response': token})
    response = r.json()
    return response['success']

def getLocationBasedDate(timestamp, cutoff_days_offset, cutoff_hours, cutoff_minutes, lat, lng):
    """
    @timestamp a UTC timestamp
    @cutoff_dats_offset +/- integer days from now that should be checking date
    @cutoff_hours integer hours for location that should be set
    @cutoff_minutes integer minutes for locaiton that should be set
    @lat float latitude of location
    @lng float longitude of location
    """
    gmaps = googlemaps.Client(key=os.environ.get("GOOGLETZAPIKEY"))
    tz_obj = gmaps.timezone(location=f"{lat},{lng}", timestamp=timestamp)
    tz_offset = tz_obj["dstOffset"] + tz_obj["rawOffset"]
    dt = datetime.utcfromtimestamp(timestamp)
    if cutoff_days_offset is not None:
        dt = dt + timedelta(days=cutoff_days_offset)
        print("X", dt.timestamp())
    if cutoff_hours is not None:
        dt = dt.replace(hour=cutoff_hours, minute=cutoff_minutes)
    print("offset:", tz_offset)
    print("Y", dt.timestamp())
    dt = dt + timedelta(minutes=tz_offset)
    print("Z", dt.timestamp())
    return dt

def isCommentAllowed(timestamp, cutoff_days_offset, cutoff_hours, cutoff_minutes, lat, lng):
    dt = getLocationBasedDate(timestamp, cutoff_days_offset, cutoff_hours, cutoff_minutes, lat, lng)
    now = datetime.now()
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
