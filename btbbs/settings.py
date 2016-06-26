#encoding:utf-8
from base_settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'btbbs',
        'USER': 'postgres',
        'PASSWORD': 'xmy5650268',
    },
    'torrent': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'torrent',
        'USER': 'root',
        'PASSWORD': 'root',
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



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/


STATIC_ROOT = os.path.join(BASE_DIR,  "static")

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
# ]
DEFAULT_FILE_STORAGE = 'qiniustorage.backends.QiniuStorage'
QINIU_ACCESS_KEY = 'jOCEgrOksRJIbggo-qp6dLujp3Vhjc7DzHmin3vs'
QINIU_SECRET_KEY = '-sn9yKeqdR7QYAVlMZZcDm4Ea44uI6sc4yc3IuJm'
QINIU_BUCKET_NAME = 'torrent'
QINIU_BUCKET_DOMAIN = '7xqsqu.com1.z0.glb.clouddn.com'
'''
# 网站相关配置
'''
DEBUG = True

STATICSITEMAPS_ROOT_SITEMAP = 'bbs.urls.search'
STATICSITEMAPS_USE_GZIP = False