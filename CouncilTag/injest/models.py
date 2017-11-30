from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=100)

class Committee(models.Model):
    name = models.CharField(max_length=250)

class Agenda(models.Model):
    meeting_time = models.PositiveIntegerField()#Unix timestamp
    committee = models.ForeignKey(Committee)

class AgendaItem(models.Model):
    title = models.TextField()
    department = models.CharField(max_length=250)
    summary = models.TextField(null=True)
    background = models.TextField(null=True)
    supplemental = models.TextField(null=True)
    sponsors = models.CharField(max_length=250, null=True)
    agenda = models.ForeignKey(Agenda, related_name='items')
    tags = models.ManyToManyField(Tag)

class AgendaRecommendation(models.Model):
    agenda_item = models.ForeignKey(AgendaItem, related_name='recommendations')
    recommendation = models.TextField()

class CommitteeMember(models.Model):
    firstname = models.CharField(max_length=250)
    lastname = models.CharField(max_length=250)
    email = models.EmailField()
    committee = models.ForeignKey(Committee, related_name='members')


class EngageUser(User):
    tags = models.ManyToManyField(Tag)


