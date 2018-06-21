from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    icon = models.CharField(max_length=100, null=True)


class EngageUser(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Committee(models.Model):
    name = models.CharField(max_length=250)
    email = models.CharField(max_length=250)


class Agenda(models.Model):
    meeting_time = models.PositiveIntegerField()  # Unix timestamp
    committee = models.ForeignKey(Committee)


class AgendaItem(models.Model):
    title = models.TextField()
    department = models.CharField(max_length=250)
    body = ArrayField(
        models.TextField(blank=True),
        default=list()
    )
    sponsors = models.CharField(max_length=250, null=True)
    agenda = models.ForeignKey(Agenda, related_name='items')
    meeting_time = models.PositiveIntegerField(default=0)  # Unix timestamp
    meeting_id = models.CharField(max_length=20, null=True)  # Agenda ID
    agenda_item_id = models.CharField(
        max_length=20, null=True)  # Agenda Item ID from server
    tags = models.ManyToManyField(Tag)


class AgendaRecommendation(models.Model):
    agenda_item = models.ForeignKey(AgendaItem, related_name='recommendations')
    recommendation = models.TextField()


class CommitteeMember(models.Model):
    firstname = models.CharField(max_length=250)
    lastname = models.CharField(max_length=250)
    email = models.EmailField()
    committee = models.ForeignKey(Committee, related_name='members')


class EngageUserProfile(models.Model):
    user = models.OneToOneField(EngageUser, on_delete=models.CASCADE)
    ethnicity = models.IntegerField(null=True, blank=True)
    zipcode = models.PositiveIntegerField(default=90401)
    verified = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)



class Message(models.Model):
    '''
    A user will input a message that will be retrieved in bulk with other
    unprocessed messges. Messages will then be grouped by item and separated 
    by pro and con and have summaries produced which gauge their sentiment 
    '''
    user = models.ForeignKey(EngageUser, null=True)
    agenda_item = models.ForeignKey(AgendaItem, null=True)
    content = models.TextField(blank=True, null=True)
    committee = models.ForeignKey(Committee, null=True)
    first_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    zipcode = models.PositiveIntegerField(default=90401)
    email = models.EmailField(blank=True, null=True)
    ethnicity = models.TextField(blank=True, null=True)
    date = models.PositiveIntegerField(default=0)  # Unix timestamp
    sent = models.PositiveIntegerField(default=0)  # Unix timestamp
    pro = models.PositiveIntegerField(default=0, null=False)
