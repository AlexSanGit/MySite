import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecuresdfdfsdfsd3423423432ds@#@!#!@$fdgsdf$@m0bi'

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '45.136.58.117']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mysitedb',
        'USER': 'userdb',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'mydb',
#         'USER': 'san',
#         'PASSWORD': '123456',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIR = [STATIC_DIR]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'