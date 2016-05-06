# encoding:utf-8
from __future__ import unicode_literals

from django.conf.urls import url

from bbs import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^detail/(?P<tid>\d+).html$', views.detail
        , name='detail'),
    url(r'^category/(?P<slug>[a-zA-Z]+).html$', views.category, name='category'),
    url(r'^download/(?P<tid>\d+)$', views.download, name='download'),
    url(r'^tag/(?P<tag>.+)$', views.tag, name='tag')
]
