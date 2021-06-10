from django.apps import AppConfig
from django.db.backends.signals import connection_created

class ApiConfig(AppConfig):
    name = 'engage.api'
