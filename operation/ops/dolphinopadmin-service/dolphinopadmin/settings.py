#! -*- coding:utf-8 -*-
# Django settings for dolphinopadmin project.
import sys
import os
import re
from django.utils.translation import ugettext_lazy as _
from ConfigParser import InterpolationMissingOptionError
from utils.parser import FreeConfigParser

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(SITE_ROOT, "../"))

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'detail': {
            'format': '%(asctime)s %(levelname)s %(name)s [%(filename)s:%(lineno)d] %(funcName)s %(message)s'
        },
        'message_only': {
            'format': '%(asctime)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'detail',
            'filename': '/tmp/dolphinopadmin.log',
            'when': 'D',
            'backupCount': 7
        },
        'perf': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'message_only',
            'filename': '/tmp/dolphinopadmin_pref.log',
            'maxBytes': 1024 * 1024 * 1024,  # 20MB
            'backupCount': 7
        },
        'err': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'detail',
            'filename': '/tmp/dolphinopadmin_service.err',
            'when': 'D',
            'backupCount': 14
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'dolphinopadmin.admin': {
            'handlers': ['file', 'err'],
            'level': 'DEBUG',
        },
        'dolphinopadmin.remotedb': {
            'handlers': ['file', 'err'],
            'level': 'DEBUG',
        },
    }
}

DEBUG = True
TEMPLATE_DEBUG = DEBUG

MEDIA_ROOT = '/var/app/data/dolphinopadmin-service'

DATABASES = None
ENV_CONFIGURATION = None
DOMAIN = None
SERVER = None


def _load_config():
    global DEBUG, TEMPLATE_DEBUG, DATABASES, ENV_CONFIGURATION, SERVER, DOMAIN, MEDIA_ROOT
    SECTION = 'dolphinopadmin-service'
    cp = FreeConfigParser()
    cp.read([os.path.join(SITE_ROOT, "../dolphinopadmin-service.cfg")])

    DEBUG = cp.getboolean(SECTION, 'debug', False)
    TEMPLATE_DEBUG = DEBUG

    DOMAIN = cp.get(SECTION, 'domain', default='ops.dolphin-browser.com')
    MEDIA_ROOT = cp.get(SECTION, 'media_root',
                        default='/var/app/data/dolphinopadmin-service')

    logs_dir = cp.get(SECTION, 'logs_dir')
    LOGGING['handlers']['file']['filename'] = os.path.join(
        logs_dir, 'dolphinopadmin.log')
    LOGGING['handlers']['perf']['filename'] = os.path.join(
        logs_dir, 'dolphinopadmin_pref.log')
    LOGGING['handlers']['err']['filename'] = os.path.join(
        logs_dir, 'dolphinopadmin.err')

    db_conf = cp.get(SECTION, 'admin_db',
                     default='172.16.9.157,dolphinopadmin,root,123456').split(',')
    DATABASES = {
        'default': {
            # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or
            # 'oracle'.
            'ENGINE': 'django.db.backends.mysql',
            # Set to empty string for localhost. Not used with sqlite3.
            'HOST': db_conf[0],
            # Or path to database file if using sqlite3.
            'NAME': db_conf[1],
            'USER': db_conf[2],                      # Not used with sqlite3.
            'PASSWORD': db_conf[3],                  # Not used with sqlite3.
            # Set to empty string for default. Not used with sqlite3.
            'PORT': '3306',
        },
    }

    SERVER = cp.get(SECTION, 'server')
    production = cp.getboolean(SECTION, 'admin_production', False)
    if production:
        envs = ('ec2', 'china', 'local')
    else:
        envs = ('local',)
    ENV_CONFIGURATION = {}
    for env in envs:
        conf_parts = re.split(
            r'[:/]', cp.get(SECTION, 'admin_env_%s' % env, default='127.0.0.1:27017/dolphinop'))
        conf_statics = cp.get(SECTION, 'web_env_%s' %
                              env, default='127.0.0.1').split(',')
        conf_domain = cp.get(SECTION, 'domain_env_%s' %
                             env, default='127.0.0.1')
        ENV_CONFIGURATION[env] = {
            'host': conf_parts[0],
            'db': conf_parts[2],
            'port': int(conf_parts[1]),
            'statics': conf_statics,
            'domain': conf_domain
        }

try:
    _load_config()
except InterpolationMissingOptionError as e:
    pass

DATABASE_ROUTERS = ['dolphinopadmin.dbpath.MyAppRouter']

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-CN'

LANGUAGES = (
    ('zh-CN', u'简体中文'),
    ('en', u'English'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/admin/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/admin/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/admin/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    #    os.path.join(os.path.dirname(__file__),'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

COMPRESS_OFFLINE = True
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'okmlf!%&1-_$q-ouj6c7k7oio84r4@f5vqregufmq@mh!dg7ne'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #    'django.template.loaders.eggs.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'dolphinopadmin.urls'

LOCALE_PATHS = (
    os.path.join(SITE_ROOT, "locale"),
)

TEMPLATE_DIRS = (
    #    os.path.join(SITE_ROOT, "templates"),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #    os.path.join(os.path.dirname(os.path.realpath(__file__)), '/feedback/templates'),
    #    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'advert/templates'),
    os.path.join(SITE_ROOT, "templates"),
)

INSTALLED_APPS = (
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'admin_enhancer',
    'dolphinopadmin.sms',
    'dolphinopadmin.usermanagement',
    'dolphinopadmin.configure',
    'dolphinopadmin.treasure',
    'dolphinopadmin.builtin',
    'dolphinopadmin.feedback',
    'dolphinopadmin.hotapps',
    'dolphinopadmin.hotappsnew',
    'dolphinopadmin.content',
    'dolphinopadmin.addon',
    'dolphinopadmin.addonstore',
    'dolphinopadmin.promotionlink',
    'dolphinopadmin.updateservice',
    'dolphinopadmin.splashscreen',
    'dolphinopadmin.subnavigation',
    'dolphinopadmin.preset',
    'dolphinopadmin.navigate',
    'dolphinopadmin.skin',
    'dolphinopadmin.advert',
    'dolphinopadmin.search',
    'dolphinopadmin.weather',
    'dolphinopadmin.desktop',
    'dolphinopadmin.gamemode',
    'dolphinopadmin.webapps',
    'dolphinopadmin.topsite',
    'dolphinopadmin.notification',
    'dolphinopadmin.push',
    'dolphinopadmin.resource',
    #'dolphinopadmin.websitesnav',

    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',
)

LEFT_NAV_MODELS = {
    'app': {
        'order': 1,
        'title': _('browsers'),
        'models': [
            'dolphinopadmin.push.*',
            'dolphinopadmin.search.*',
            'dolphinopadmin.skin.*',
            'dolphinopadmin.builtin.*',
            'dolphinopadmin.feedback.*',
            'dolphinopadmin.treasure.*',
            'dolphinopadmin.configure.*',
            'dolphinopadmin.content.*',
            'dolphinopadmin.addon.*',
            'dolphinopadmin.promotionlink.*',
            'dolphinopadmin.updateservice.*',
            'dolphinopadmin.splashscreen.*',
            'dolphinopadmin.preset.*',
            'dolphinopadmin.weather.*',
            'dolphinopadmin.desktop.*',
            'dolphinopadmin.gamemode.*',
            'dolphinopadmin.advert.*',
            'dolphinopadmin.topsite.*',
            'dolphinopadmin.notification.*',
            'dolphinopadmin.sms.*',
            #'dolphinopadmin.websitesnav.*',
        ],
        'app_label_order': {    # use to control the order of leftnav
            'push':  1,
            'search': 2,
            'skin': 3,
            'treasure': 4,
            'desktop': 5,
            'splashscreen': 6,
            'promotionlink': 7,
            'preset': 8,
            'content': 9,
            'builtin': 10,
            'notification': 11,
            'updateservice': 12,
            'gamemode': 13,
            'weather': 14,
            'feedback': 15,
            'addon': 16,
            'advert': 17,
            'topsite': 18,
            'configure': 19,
            'sms': 20,
            #'websitesnav': 21,
        }
    },
    'resource': {
        'order': 2,
        'title': _('static file'),
        'models': [
            'dolphinopadmin.resource.*'
        ],
        'app_label_order': {
            'resource': 1,
            #'icon':2,
        }
    },
    'webpage': {
        'order': 3,
        'title': _('webpage'),
        'models': [
            'dolphinopadmin.base.base_model.*',
            'dolphinopadmin.webapps.*',
            'dolphinopadmin.subnavigation.*',
            'dolphinopadmin.navigate.*',
            'dolphinopadmin.addonstore.*',
            'dolphinopadmin.hotapps.*',
            'dolphinopadmin.hotappsnew.*',
        ],
        'app_label_order': {
            'webapps': 1,
            'hotappsnew': 2,
            'navigate': 3,
            'subnavigation': 4,
            'addonstore': 5,
            'hotapps': 6,
        }
    },
    'setting': {
        'order': 4,
        'title': _('authority manage'),
        'models': [
            'django.contrib.admin.models.LogEntry',
            'dolphinopadmin.usermanagement.*'
        ],
        'app_label_order': {
            'usermanagement': 1,
            'admin': 2,
        }
    }
}
