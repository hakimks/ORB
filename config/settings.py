# -*- coding: utf-8 -*-

"""
Django settings for mpowering project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os

from django.core.urlresolvers import reverse_lazy

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

SECRET_KEY = '*****************************'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']

ADMINS = (
    ('Admin', 'org@example.com'),
)

SITE_ID = 1

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'


INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'crispy_forms',
    'tastypie',
    'tinymce',
    'django_wysiwyg',
    'haystack',
    'sorl.thumbnail',
    'orb',
    'orb.courses',
    'orb.peers',
    'orb.review',
    'orb.analytics',
    'orb.toolkits',
    'modeltranslation_exim',
    'django_extensions',
]


MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'orb.middleware.SearchFormMiddleware',
]


#####################################################################
# Templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'orb.context_processors.get_menu',
                'orb.context_processors.get_version',
                'orb.context_processors.base_context_processor',
            ],
            'debug': DEBUG,
        },
    },
]

#####################################################################


#####################################################################
# Database configuration
# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # you can use your preferred one though
        'NAME': 'orb',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1', #leave empty for default
        'PORT': '', #leave empty for default
    }
}
#####################################################################


#####################################################################
# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'orb/locale'),
]
gettext = lambda s: s  # noqa
LANGUAGES = [
    ('en', u'English'),
    ('es', u'Español'),
    ('pt-br', u'Português'),
]
MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
#####################################################################
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATICFILES_DIRS = [os.path.join(ROOT_DIR, 'static')]



STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

#####################################################################
# Static assets & media uploads
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
#####################################################################


#####################################################################
# Email
SERVER_EMAIL = 'ORB <orb@example.com>'
EMAIL_SUBJECT_PREFIX = '[ORB]: '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_FILE_PATH = '/tmp/'
#####################################################################


#####################################################################
# Search settings
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr'
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

ADVANCED_SEARCH_CATEGORIES = [
    ('health_topic', 'health-domain'),
    ('resource_type', 'type'),
    ('audience', 'audience'),
    ('geography', 'geography'),
    ('language', 'language'),
    ('device', 'device'),
]
#####################################################################


#####################################################################
# Authentication
LOGIN_URL = reverse_lazy('profile_login')
AUTHENTICATION_BACKENDS =  [
    'orb.auth.UserModelEmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]
#####################################################################


#####################################################################
# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['console'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'orb': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
#####################################################################


#####################################################################
# ORB specific settings
ORB_RESOURCE_DESCRIPTION_MAX_WORDS = 150
ORB_GOOGLE_ANALYTICS_CODE = ''
ORB_INFO_EMAIL = 'orb@example.com'
ORB_PAGINATOR_DEFAULT = 20
ORB_RESOURCE_MIN_RATINGS = 3
TASK_UPLOAD_FILE_TYPE_BLACKLIST = [u'application/vnd.android']
TASK_UPLOAD_FILE_MAX_SIZE = "5242880"
STAGING = False  # used for version context processor
#####################################################################


DJANGO_WYSIWYG_FLAVOR = "tinymce_advanced"
CRISPY_TEMPLATE_PACK = 'bootstrap3'

TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced", # default value
    'relative_urls': False, # default value
    'width': '100%',
    'height': 300,
    'position': 'top',
}

# Simple settings flags for download features
DOWNLOAD_LOGIN_REQUIRED = True
DOWNLOAD_EXTRA_INFO = True


try:
    from local_settings import *  # noqa
except ImportError:
    import warnings
    warnings.warn("Using default settings. Add `config.local_settings.py` for custom settings.")
