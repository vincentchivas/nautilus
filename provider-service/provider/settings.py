import os
from ConfigParser import ConfigParser

EXCEPTION_DEBUG = False
AUTH_DEBUG = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

BUILD_SERVICE_URI = 'http://172.16.77.22:8080/buildservice/'

DBS = {
    'default': {
        'ENGINE': 'mysql',
        'NAME': 'providerdb',
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '123456',                  # Not used with sqlite3.
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '172.16.7.14',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '3306',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# STATIC_ROOT = os.path.join(
#    os.path.abspath(os.path.dirname(__file__)), 'static')
STATIC_ROOT = '/var/app/data/provider-service'

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

CUS_TEMPLATE_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'templates')

HOST = "172.16.7.14"

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
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

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1a53ngk0aii@t$+dfwz5rrjwff_3txa639vs8fx(l!fwv#rt$7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'provider.middleware.LogMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'provider.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'provider.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
            '%(thread)d %(message)s'
        },
        'detail': {
            'format': '%(asctime)s %(levelname)s %(module)s %(name)s '
            '[%(filename)s:%(lineno)d] %(funcName)s %(message)s'
        },
        'message_only': {
            'format': '%(asctime)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'provider': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'detail',
            'filename': '/tmp/provider.log',
            'when': 'D',
            'backupCount': 7
        },
        'model': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'detail',
            'filename': '/tmp/model.log',
            'when': 'D',
            'backupCount': 7
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'detail',
            'filename': '/tmp/error.log',
            'when': 'D',
            'backupCount': 7
        },
        'db': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'detail',
            'filename': '/tmp/db.log',
            'when': 'D',
            'backupCount': 7
        },
        'apk': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'detail',
            'filename': '/tmp/apk.log',
            'when': 'D',
            'backupCount': 7
        },
        'getapi': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'detail',
            'filename': '/tmp/get_api.log',
            'when': 'D',
            'backupCount': 7
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'provider': {
            'handlers': ['provider', 'error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'model': {
            'handlers': ['provider', 'model', 'error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'db': {
            'handlers': ['db', 'error'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'apk': {
            'handlers': ['apk', 'provider'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'getapi': {
            'handlers': ['getapi', 'provider'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

APK_PATH = '/tmp/'
APPEND_SLASH = False
ADAPTER_MAP_PATH = os.path.join(STATIC_ROOT, "adapter_map.xlsx")
DB_CONN_STR = None

LOGS_DIR = "/tmp/"

SECTION = 'provider-service'


def _load_service_config(cp):
    global DB_CONN_STR, LOGS_DIR, HOST, AUTH_DEBUG, EXCEPTION_DEBUG
    DB_CONN_STR = cp.get(SECTION, 'db_conn_str')
    LOGS_DIR = cp.get(SECTION, 'logs_dir')
    HOST = cp.get(SECTION, 'host')
    AUTH_DEBUG = cp.getboolean(SECTION, 'auth_debug_value')
    EXCEPTION_DEBUG = cp.getboolean(SECTION, 'exception_debug_value')

    for k, v in LOGGING['handlers'].iteritems():
        if 'filename' in v:
            v['filename'] = os.path.join(
                LOGS_DIR, os.path.basename(v['filename']))


cp = ConfigParser()
cp.read([os.path.join(SITE_ROOT, "provider-service.cfg")])
_load_service_config(cp)
