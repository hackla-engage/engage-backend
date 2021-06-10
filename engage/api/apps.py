from django.apps import AppConfig
from django.db.backends.signals import connection_created

def activate_foreign_keys(sender, connection, **kwargs):
    """Enable integrity constraint with sqlite."""
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')

class ApiConfig(AppConfig):
    name = 'engage.api'
    def ready(self):
        connection_created(activate_foreign_keys)