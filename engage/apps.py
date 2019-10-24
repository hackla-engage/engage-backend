from django.apps import AppConfig
import json
import logging
from engage import settings
import pytz
from datetime import datetime, timedelta

log = logging.Logger(__name__)


class engageConfig(AppConfig):
    name = 'engage'

    def ready(self):
        pass