from django.apps import AppConfig

class InjestConfig(AppConfig):
    name = 'injest'
    def ready(self):
        print("HELLO")