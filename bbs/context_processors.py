#encoding:utf-8

from django.template.context_processors import request


def site(request):
    return {
        'DOMAIN': '',
        'SITE_NAME': '',

    }

def movie(request):
    pass