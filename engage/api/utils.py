from engage import settings
from datetime import datetime, timedelta
import logging
import requests
import os
import bcrypt
import base64
import pytz
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
log = logging.Logger(__name__)
if not settings.TEST:
    ses_client = boto3.client('ses', aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                              aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                              region_name=os.environ["AWS_REGION"])
    if settings.DEBUG:
        log.error("{}\n {}\n  {}".format(os.getenv("AWS_ACCESS_KEY_ID"),
                                        os.getenv("AWS_SECRET_ACCESS_KEY"), os.getenv("AWS_REGION")))


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


def isCommentAllowed(timestamp):
    dt = datetime.now().timestamp()
    if dt > timestamp:
        return False
    return True


def send_mail(mail_message):
    if type(mail_message["user"]) is dict:
        to_email = mail_message["user"]["email"]
    else:
        to_email = mail_message["user"].email
    multipart_content_subtype = 'mixed'
    msg = MIMEMultipart(multipart_content_subtype)
    msg['Subject'] = mail_message["subject"]
    msg['To'] = to_email
    msg['From'] = 'do-not-reply@engage.town'
    part = MIMEText(mail_message['content'], 'html')
    msg.attach(part)
    if "attachment_file_path" in mail_message:
        with open(mail_message["attachment_file_path"], 'rb') as f:
            part = MIMEApplication(f.read(), _subtype='pdf')
            part.add_header('Content-Disposition', 'attachment',
                            filename=mail_message['attachment_file_name'])
            msg.attach(part)
    try:
        if settings.DEBUG:
            log.error(("YYY", msg.as_string()))
        if not settings.TEST:
            response = ses_client.send_raw_email(
                Source="engage team <do-not-reply@engage.town>",
                Destinations=[to_email],
                RawMessage={'Data': msg.as_string()})
            if response['MessageId'] is not None:
                return True
            else:
                log.error("Could not send an email from {} to {} about {}".format("do-not-reply@engage.town",
                                                                                  to_email, mail_message['Subject']))
                return False
        else:
            return True
    except Exception as exc:
        log.error("Could not send email and threw error")
        log.error(exc)
        return False
