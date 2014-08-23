from django.conf import settings
from dolphinop.db import config, content

DB = settings.DOLPHINOP_DB

config(content, **DB)
