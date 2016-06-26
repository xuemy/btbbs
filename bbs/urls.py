# encoding:utf-8
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.contrib.sitemaps import GenericSitemap
from django.views.decorators.cache import cache_page

from bbs import sitemap
from bbs import views
from bbs.models import Movie

class LimitSitemap(GenericSitemap):
    limit = 1000

class SearchSitemap(GenericSitemap):
    limit = 2000
    sitemap_template = 'bbs/search_comment.xml'

sitemaps = {
    'movie': LimitSitemap({'queryset': Movie.objects.all(), 'date_field': 'ctime'}, priority=0.6),
}

search = {
    'search': SearchSitemap({'queryset': Movie.objects.exclude(genres__exact=[]).all(), 'date_field': 'ctime'}, priority=0.8),
}

urlpatterns = [
    url(r'^$', views.Index.as_view() , name='index'),

    url(r'^detail/(?P<douban_id>\d+).html$', cache_page(60 * 60)(views.Detail.as_view()), name='detail'),

    url(r'^download/(?P<tid>\d+)$', cache_page(60 * 60)(views.download), name='download'),

    url(r'^t/(?P<tag_name>.+)$', cache_page(60 * 60)(views.Tag.as_view()), name='tag'),

    url(r'^genres/(?P<name>.+)$', cache_page(60 * 60)(views.Genres.as_view()), name='genres'),

    url(r'^genres$', cache_page(60 * 60)(views.all_genres), name='all_genres'),

    # url(r'^data/(?P<data>(cast)|(writer)|(director)|(genre)|(country))/(?P<name>.+)$', views.Data.as_view(), name='data'),
    # url(r'^data/country/(?P<name>.+)$', views.DateCountry.as_view(), name='country'),




    url(r'sitemap\.xml$',
        cache_page(86400)(sitemap.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}
        ),

    url(r'sitemap-(?P<section>.+)-(?P<page>\d+)\.xml',
        cache_page(86400)(sitemap.sitemap),
        {'sitemaps': sitemaps},
        name='sitemaps'
        ),


    url(r'search\.xml', include('static_sitemaps.urls')),

    # url(r'search\.xml', sitemap.search_index, {'sitemaps': search, 'sitemap_url_name':'search'}),
    # url(r'search-(?P<section>.+)-(?P<page>\d+)\.xml', cache_page(24 * 60 * 60)(sitemap.search_sitemap), {'sitemaps': search}, name='search')
]
