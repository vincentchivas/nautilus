# -*- coding:utf-8 -*-
import os
import json
import re
import logging.config
# from provisionadmin_service.model.base import ModelBase

from armory.marine.parser import FreeConfigParser


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))


# firstly, load config file to initialize constant
SECTION = 'cm-console-service'
cp = FreeConfigParser()
cp.read([os.path.join(SITE_ROOT, "conf/online.cfg")])

DEBUG = cp.getboolean(SECTION, 'debug', default=True)
EXCEPTION_DEBUG = cp.getboolean(SECTION, 'exception_debug', default=False)
MONGO_CONFIG = cp.get(SECTION, 'mongo_config', default=None)
LOG_ROOT = cp.get(SECTION, 'log_root', default='/tmp')
LOG_FILE = os.path.join(LOG_ROOT, 'online_admin.log')
LOG_ERR_FILE = os.path.join(LOG_ROOT, 'online_admin.err')
PAGE_LIMIT = cp.get(SECTION, 'page_limit', default=10)
HTTP_PORT = cp.get(SECTION, 'http_port', default=6000)

HOST = cp.get(SECTION, 'host')
RULE_SERVICE_HOST = cp.get(SECTION, 'rule_service_host')
AUTH_SERVICE_HOST = cp.get(SECTION, 'auth_service_host')
RESOURCE_SERVICE_HOST = cp.get(SECTION, 'resource_service_host')

# upload environment local ec2
production = cp.getboolean(SECTION, 'admin_production')
envs = ('ec2', 'local') if production else ('local', )
REMOTEDB_SETTINGS = {}
for env in envs:
    conf_parts = re.split(r'[:/]', cp.get(SECTION, 'db_conn_%s' % env))
    conf_statics = cp.get(SECTION, 'web_env_%s' % env).split(',')
    # config with ','
    conf_domain = cp.get(SECTION, 'domain_env_%s' % env)
    conf_s3 = cp.get(SECTION, 's3_env_%s' % env)
    REMOTEDB_SETTINGS[env] = {
        'host': conf_parts[0],
        'name': conf_parts[2],
        'port': int(conf_parts[1]),
        'statics': conf_statics,
        'domain': conf_domain,
        's3_remote': conf_s3}


S3_DOMAIN = 'http://opsen-static.dolphin-browser.com/'

API_PREF = '/common'

# secondly, construct logging config dict
LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(process)d %(levelname)s %(asctime)s %(message)s'
        },
        'detail': {
            'format': '%(process)d %(levelname)s %(asctime)s '
            '[%(module)s.%(funcName)s line:%(lineno)d] %(message)s',
        },
    },
    'handlers': {
        'cm_console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_FILE,
        },
        'err_file': {
            'level': 'WARN',
            'formatter': 'detail',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': LOG_ERR_FILE,
        },
    },
    'loggers': {
        'cm_console': {
            'handlers': ['cm_console', 'file', 'err_file'
                         ] if DEBUG else ['file', 'err_file'],
            'level': 'DEBUG',
            'propagate': True
        },
        'armory': {
            'handlers': ['cm_console', 'file', 'err_file'
                         ] if DEBUG else ['file', 'err_file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# lastly, config logging
logging.config.dictConfig(LOGGING_DICT)

# besides init models from models.cfg
global MODELS
f = file(os.path.join(SITE_ROOT, "models.cfg"))
MODELS = json.load(f)

# other configs
MEDIA_ROOT = '/var/app/data/cm_console'
TMPL_FOLDER = '/var/app/enabled/cm_console_service/cm_console/webfront/templates'
