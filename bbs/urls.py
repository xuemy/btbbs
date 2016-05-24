# encoding:utf-8
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.sitemaps import GenericSitemap
from django.views.decorators.cache import cache_page

from bbs import sitemap
from bbs.models import Movie
from bbs.views import category
from bbs.views import detail
from bbs.views import download
from bbs.views import index
from bbs.views import tag

class LimitSitemap(GenericSitemap):
    limit = 500


sitemaps = {
    'movie': LimitSitemap({'queryset': Movie.objects.all(), 'date_field': 'ctime'}, priority=0.6),
}

urlpatterns = [
    url(r'^$', index.index , name='index'),

    url(r'^detail/(?P<tid>\d+).html$', detail.V.as_view(), name='detail'),

    url(r'^download/(?P<tid>\d+)$', download.view, name='download'),

    url(r'^tag/(?P<tag_name>.+)$', tag.Tag.as_view(), name='tag'),

    url(r'^(?P<category>[tvmovie])', category.Category.as_view(), name='category'),



    url(r'sitemap\.xml$',
        cache_page(86400)(sitemap.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(r'sitemap-(?P<section>.+)-(?P<page>\d+)\.xml',
        cache_page(86400)(sitemap.sitemap),
        {'sitemaps': sitemaps}, name='sitemaps'),
]
