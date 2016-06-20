#encoding:utf-8

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'btbbs',
        'USER': 'postgres',
        'PASSWORD': 'xmy5650268',
        # 'OPTIONS': {'charset':'utf8mb4'}
        # 'HOST':'127.0.0.1',
    },
    'torrent': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'torrent',
        'USER': 'root',
        'PASSWORD': 'root',
        # 'OPTIONS': {'charset':'utf8mb4'}
        'HOST': '127.0.0.1',
    },
    'bt2020': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bt2020',
        'USER': 'postgres',
        'PASSWORD': 'xmy5650268',
        # 'OPTIONS': {'charset':'utf8mb4'}
        # 'HOST':'127.0.0.1',
    },
}


STATIC_ROOT = '/var/bt2020/static'
DEBUG = False
ALLOWED_HOSTS = ['bt2020.com', 'www.bt2020.com']

SITE_NAME = 'bt2020.com'
SITE_URL = ''
SITE_DESCRIPTION = ''
SITE_KEYWORDS = ''