from django.apps import AppConfig
import json
import logging
from CouncilTag.settings import TEST, DEBUG, r
import pytz
from datetime import datetime, timedelta

log = logging.Logger(__name__)


class CouncilTagConfig(AppConfig):
    name = 'CouncilTag'

    def ready(self):
        pass