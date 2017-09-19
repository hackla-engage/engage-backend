from django.db import models

# Create your models here.
class Committee(models.Model):
    name = models.CharField(max_length=250)

class Agenda(models.Model):
    meeting_time = models.PositiveIntegerField()#Unix timestamp
    committee = models.ForeignKey(Committee)

class AgendaItem(models.Model):
    title = models.TextField()
    department = models.CharField(max_length=250)
    summary = models.TextField()
    background = models.TextField()
    supplemental = models.TextField()
    sponsors = models.CharField(max_length=250)
    agenda = models.ForeignKey(Agenda)

class AgendaRecommendation(models.Model):
    agenda_item = models.ForeignKey(AgendaItem)
    recommendation = models.TextField()




