"""
Django settings for massenergize_portal_backend project.

Generated by 'django-admin startproject' using Django 2.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

from _main_.utils.utils import is_test_mode
from .utils.stage import Stage
import boto3

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ********  LOAD CONFIG DATA ***********#
# DJANGO_ENV can be passed in through the makefile, with "make start env=local"
DJANGO_ENV = os.environ.get("DJANGO_ENV", "dev")

STAGE = Stage(DJANGO_ENV)
os.environ.update(STAGE.get_secrets())

# Database selection, development DB unless one of these chosen
IS_PROD = STAGE.is_prod()
IS_CANARY = STAGE.is_canary()
IS_LOCAL = STAGE.is_local()

RUN_SERVER_LOCALLY = IS_LOCAL
RUN_CELERY_LOCALLY = IS_LOCAL

if is_test_mode():
    RUN_CELERY_LOCALLY = True

# ********  END LOAD CONFIG DATA ***********#

SECRET_KEY =  os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = RUN_SERVER_LOCALLY

ALLOWED_HOSTS = [
    '*',
    '0.0.0.0',
    '127.0.0.1',
    'localhost:3000',
    'localhost',
    '.massenergize.org',
    '.massenergize.com',
    '.massenergize.dev',
    '.massenergize.test',
    'MassenergizeApi-env.eba-zfppgz2y.us-east-2.elasticbeanstalk.com',
    'ApiDev-env.eba-5fq2r9ph.us-east-2.elasticbeanstalk.com',
    'dev-api-env.eba-nfqpwkju.us-east-2.elasticbeanstalk.com',
    'massenergize-canary-api.us-east-2.elasticbeanstalk.com',
    'massenergize.test',
    'massenergize.test:3000',
]

if RUN_SERVER_LOCALLY:
    ALLOWED_HOSTS = ['*']
    

INSTALLED_APPS = [
    'django_hosts',
    'authentication',
    'carbon_calculator',
    'database',
    'api',
    'website',
    "task_queue",
    'django_celery_beat',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "apps__campaigns"
]

MIDDLEWARE = [
    'cid.middleware.CidMiddleware',
    'django_hosts.middleware.HostsRequestMiddleware',
    'authentication.middleware.RemoveHeaders',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #custom middlewares
    'authentication.middleware.MassenergizeJWTAuthMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
    '_main_.utils.metrics.middleware.MetricsMiddleware'
]


#-------- FILE STORAGE CONFIGURATION ---------------------#
if not is_test_mode():
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE  = 'storages.backends.s3boto3.S3Boto3Storage'
#-------- FILE STORAGE CONFIGURATION ---------------------#


#-------- AWS CONFIGURATION ---------------------#
AWS_ACCESS_KEY_ID        = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY    = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME  = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_SIGNATURE_VERSION = os.environ.get('AWS_S3_SIGNATURE_VERSION')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_DEFAULT_ACL  = None
AWS_QUERYSTRING_AUTH = False

#-------- OTHER CONFIGURATION ---------------------#
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
USE_X_FORWARDED_HOST = True

WSGI_APPLICATION = '_main_.wsgi.application'
# ASGI_APPLICATION = '_main_.asgi.application'

X_FRAME_OPTIONS = 'SAMEORIGIN'

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = not DEBUG
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_DEFAULT_ACL = None
APPEND_SLASH = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440*3

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]




# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE'   : os.environ.get('DATABASE_ENGINE'),
        'NAME'     : os.environ.get('DATABASE_NAME'),
        'USER'     : os.environ.get('DATABASE_USER'),
        'PASSWORD' : os.environ.get('DATABASE_PASSWORD'),
        'HOST'     : os.environ.get('DATABASE_HOST'),
        'PORT'     : os.environ.get('DATABASE_PORT')
    },
    'test_db': {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": 'test.sqlite3',
    }
}

if is_test_mode():
    DATABASES['default'] = DATABASES['test_db']

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.db.DatabaseCache",
#         "LOCATION": "main_cache_table",
#     }
# }

# url and hosts config
ROOT_URLCONF = '_main_.urls'
ROOT_HOSTCONF = '_main_.hosts'
DEFAULT_HOST = 'main'

# firebase setup
FIREBASE_CREDENTIALS = credentials.Certificate(STAGE.get_firebase_auth())

firebase_admin.initialize_app(FIREBASE_CREDENTIALS)


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


### Begin Logger setttings ####
CID_GENERATE = True
CID_CONCATENATE = True
LOGGING = STAGE.get_logging_settings()


### End Logger settings ###

# Sentry Logging Initialization
sentry_dsn = os.environ.get('SENTRY_DSN')
if sentry_dsn:
  sentry_sdk.init(
    dsn=sentry_dsn,
    integrations=[DjangoIntegration(
            transaction_style='url',
            middleware_spans=True,
        ),
           CeleryIntegration(),
    ],
    traces_sample_rate=1.0,


    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
  )

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True 
EMAIL_HOST = 'smtp.gmail.com' 
EMAIL_PORT = 587 
EMAIL_HOST_USER = os.environ.get('EMAIL')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
POSTMARK_EMAIL_SERVER_TOKEN = os.environ.get('POSTMARK_EMAIL_SERVER_TOKEN')
POSTMARK_DOWNLOAD_SERVER_TOKEN = os.environ.get('POSTMARK_DOWNLOAD_SERVER_TOKEN')
SLACK_COMMUNITY_ADMINS_WEBHOOK_URL = os.environ.get('SLACK_COMMUNITY_ADMINS_WEBHOOK_URL')
SLACK_SUPER_ADMINS_WEBHOOK_URL = os.environ.get('SLACK_SUPER_ADMINS_WEBHOOK_URL')
POSTMARK_ACCOUNT_TOKEN = os.environ.get('POSTMARK_ACCOUNT_TOKEN')


TEST_DIR = 'test_data'
TEST_PASSPORT_KEY = os.environ.get('TEST_PASSPORT_KEY')


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
if is_test_mode():
    MEDIA_ROOT = os.path.join(BASE_DIR, TEST_DIR, 'media')
    STATIC_ROOT = os.path.join(BASE_DIR, TEST_DIR, 'static')
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Simplified static file serving.
STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'