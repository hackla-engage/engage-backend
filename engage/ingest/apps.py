from django.apps import AppConfig

class IngestConfig(AppConfig):
    name = 'engage.ingest'
    def ready(self):
        print("HELLO")