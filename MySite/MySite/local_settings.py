import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-)a9i=uwe2%=w1y1s^0^2ndrxtje7n$2h6=b+v0$0@)3=$@m0bi'

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIR = [STATIC_DIR]
