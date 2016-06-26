#encoding:utf-8
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bt2020',
        'USER': 'bt2020',
        'PASSWORD': 'bt2020@xmy#5650268',
    },
}


STATIC_ROOT = '/home/bt2020/static'
DEBUG = False
ALLOWED_HOSTS = ['bt2020.com', 'www.bt2020.com']

SITE_NAME = 'bt2020.com'
SITE_URL = ''
SITE_DESCRIPTION = ''
SITE_KEYWORDS = ''


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

STATICSITEMAPS_ROOT_SITEMAP = 'bbs.urls.search'
STATICSITEMAPS_USE_GZIP = False