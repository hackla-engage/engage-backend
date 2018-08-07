from PyPDF2 import PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from CouncilTag.ingest.models import Message
import io
from datetime import datetime, date
import os
from CouncilTag.ingest.sendEmail import sendEmail




def paragraphize_comments(comments, contents):
    ps_email = ParagraphStyle(
        "Email", fontSize=10, leftIndent=0.25 * inch, textColor="#000000")
    ps_comment = ParagraphStyle(
        "Comment", fontSize=10, leftIndent=0.25 * inch, textColor="#000000")
    for comment in comments:
        if comment.email is not None:
            email = "Email: " + comment.email
            comment = "Comment: " + comment.content
        elif comment.user is not None:
            email = "Email: " + comment.user.email
            comment = "Comment: " + comment.content
        else:
            continue
        contents.append(Paragraph(email, ps_email))
        contents.append(Paragraph(comment, ps_comment))
    return contents


def writePdfForAgendaItems(agenda_items):
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    static = 'PDF_Reports'
    full_path = os.path.join(root_dir,static)
    today = datetime.today()

    if not os.path.exists(full_path):
        os.mkdir(full_path)

    try:
        doc = SimpleDocTemplate(str(full_path) + "/Meeting_" + str(datetime.fromtimestamp(agenda_items[0].agenda.meeting_time).strftime('%Y%m%d')) + f"_{today.strftime('%Y%m%d')}.pdf",
                                pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        contents = []

        # Paragraph styles
        ps_title = ParagraphStyle(
            "title", fontSize=14, alignment=TA_JUSTIFY, spaceAfter=0.2 * inch)
        ps_id = ParagraphStyle("id", fontSize=10)
        ps_pro = ParagraphStyle(
            'pro', fontSize=10, backColor='#0000FF', textColor="#FFFFFF")
        ps_con = ParagraphStyle(
            'con', fontSize=10, backColor='#FF0000', textColor='#FFFFFF')
        ps_need_info = ParagraphStyle(
            'need_info', fontSize=10, backColor='#000000', textColor='#FFFFFF')
        
        for upcoming_agenda_item in agenda_items:
            contents.append(
                Paragraph("Title: " + upcoming_agenda_item.title, ps_title))
            contents.append(
                Paragraph("ID: " + upcoming_agenda_item.agenda_item_id, ps_id)
            )
            pro_comments_on_agenda_item = Message.objects.filter(
                agenda_item=upcoming_agenda_item, pro=0
            )
            con_comments_on_agenda_item = Message.objects.filter(
                agenda_item=upcoming_agenda_item, pro=1
            )
            need_info_comments_on_agenda_item = Message.objects.filter(
                agenda_item=upcoming_agenda_item, pro=2
            )
            contents.append(Paragraph("Pro comments", ps_pro))
            contents.append(Spacer(1, 0.2 * inch))
            paragraphize_comments(pro_comments_on_agenda_item, contents)
            contents.append(Spacer(1, 0.5 * inch))
            contents.append(Paragraph("Con comments", ps_con))
            contents.append(Spacer(1, 0.2 * inch))
            paragraphize_comments(con_comments_on_agenda_item, contents)
            contents.append(Spacer(1, 0.5 * inch))
            contents.append(
                Paragraph("Need more information comments", ps_need_info))
            contents.append(Spacer(1, 0.2 * inch))
            paragraphize_comments(need_info_comments_on_agenda_item, contents)
            contents.append(Spacer(1, 0.5 * inch))
            contents.append(PageBreak())
        doc.build(contents)

        attachment = str(full_path) + "/Meeting_" + str(datetime.fromtimestamp(agenda_items[0].agenda.meeting_time).strftime('%Y%m%d')) + f"_{today.strftime('%Y%m%d')}.pdf"
        attachment_type = "application/pdf"
        email_body = f"Greetings from engage Santa Monica.\n\nPlease find attached the comment submissions for the {datetime.fromtimestamp(agenda_items[0].agenda.meeting_time).strftime('%m/%d/%Y')} Council meeting for {today.strftime('%Y-%m-%d')}.\n\nFor any questions, please contact engage@engage.town.\n\nYour Engage team."
        subject = f"Council Meeting {datetime.fromtimestamp(agenda_items[0].agenda.meeting_time).strftime('%m/%d/%Y')} - Comment Submission {today.strftime('%Y-%m-%d')}"
        sender = 'engage@engage.town'
        recipient = ['teddy.crepineau@gmail.com']
        
        sendEmail(subject, email_body, sender, recipient, attachment, attachment_type)
        
        return True
    except:
        return False