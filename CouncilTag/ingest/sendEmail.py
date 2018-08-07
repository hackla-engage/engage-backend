from django.core import mail

def sendEmail(subject, message, sender, recipient, attachment=None, attachment_type=None):
    try:
        connection = mail.get_connection()
    except:
        raise

    if not subject:
        raise ValueError("Error while parsing the arguments. Please make sure to provide a subject")
    if not message:
        raise ValueError("Error while parsing the arguments. Please make sure to provide a message")
    if not sender:
        raise ValueError("Error while parsing the arguments. Please make sure to provide an email for sender")
    if not recipient:
        raise ValueError("Error while parsing the arguments. Please make sure to provide a list contain emails for the recipients")
            
    email = mail.EmailMessage(subject, message, sender, recipient,  connection=connection)
    email.attach_file(attachment, attachment_type)

    try:
        email.send()
        return True
    except:
        raise