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


def paragraphize_comments(comments, contents):
    ps_email = ParagraphStyle(
        "email", fontSize=10, leftIndent=0.25 * inch, textColor="#0000FF")
    ps_comment = ParagraphStyle(
        "comment", fontSize=10, leftIndent=0.25 * inch, textColor="#00FF00")
    for comment in comments:
        if comment.email is not None:
            email = "email: " + comment.email
            comment = "comment: " + comment.content
        elif comment.user is not None:
            email = "email: " + comment.user.email
            comment = "comment: " + comment.content
        else:
            continue
        contents.append(Paragraph(email, ps_email))
        contents.append(Paragraph(comment, ps_comment))
    return contents


def writePdfForAgendaItems(agenda_items):
    try:
        doc = SimpleDocTemplate(str(agenda_items[0].agenda.meeting_time) + ".pdf",
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
        print("DONE")
        return True
    except:
        return False
