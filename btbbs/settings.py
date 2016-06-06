#encoding:utf-8

"""
Django settings for btbbs project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8g$3dmk@au*ek@40-hx5av49skn8i1999mwtl@&f_$xi3kr1-('

# SECURITY WARNING: don't run with debug turned on in production!

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',

    'taggit',
    'bbs',
    # 'pagination',
]


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'pagination.middleware.PaginationMiddleware',
]

ROOT_URLCONF = 'btbbs.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'bbs.context_processors.site',
                # 'bbs.context_processors.movie',
            ],
        },
    },
]

WSGI_APPLICATION = 'btbbs.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'btbbs',
        'USER':'postgres',
        'PASSWORD':'xmy5650268',
        # 'OPTIONS': {'charset':'utf8mb4'}
        # 'HOST':'127.0.0.1',
    },
    'torrent': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'torrent',
        'USER':'root',
        'PASSWORD':'root',
        # 'OPTIONS': {'charset':'utf8mb4'}
        'HOST':'127.0.0.1',
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR,  "static")

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
# ]

DEFAULT_FILE_STORAGE = 'qiniustorage.backends.QiniuStorage'
QINIU_ACCESS_KEY ='jOCEgrOksRJIbggo-qp6dLujp3Vhjc7DzHmin3vs'
QINIU_SECRET_KEY = '-sn9yKeqdR7QYAVlMZZcDm4Ea44uI6sc4yc3IuJm'
QINIU_BUCKET_NAME = 'torrent'
QINIU_BUCKET_DOMAIN = '7xqsqu.com1.z0.glb.clouddn.com'
'''
# 网站相关配置
'''
DEBUG = True

SITE_NAME = 'bt2020.com'
SITE_URL = ''
SITE_DESCRIPTION = ''
SITE_KEYWORDS = ''



if DEBUG:
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = ['bt2020.com', 'www.bt2020.com']

TV_TAGS = ["美剧", "英剧", "韩剧", "日剧", "国产剧", "港剧", "日本动画"]
MOVIE_TAGS = ["热门", "最新", "经典", "可播放", "豆瓣高分", "冷门佳片", "华语", "欧美", "韩国", "日本", "动作", "喜剧", "爱情", "科幻", "悬疑", "恐怖", "治愈"]
