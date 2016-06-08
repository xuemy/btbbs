# encoding:utf-8
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib.sitemaps import GenericSitemap
from django.views.decorators.cache import cache_page

from bbs import sitemap
from bbs import views
from bbs.models import Movie

class LimitSitemap(GenericSitemap):
    limit = 2000


sitemaps = {
    'movie': LimitSitemap({'queryset': Movie.objects.all(), 'date_field': 'ctime'}, priority=0.6),
}

urlpatterns = [
    url(r'^$', views.Index.as_view() , name='index'),

    url(r'^detail/(?P<douban_id>\d+).html$', views.Detail.as_view(), name='detail'),

    url(r'^download/(?P<tid>\d+)$', views.download, name='download'),

    url(r'^t/(?P<tag_name>.+)$', views.Tag.as_view(), name='tag'),

    url(r'^genres/(?P<name>.+)$', views.Genres.as_view(), name='genres'),

    url(r'^genres$', views.all_genres, name='all_genres'),
    # url(r'^genre/(?P<genre>.+)$', views.Genre.as_view(), name='genre'),

    # url(r'^data/(?P<data>(cast)|(writer)|(director)|(genre)|(country))/(?P<name>.+)$', views.Data.as_view(), name='data'),
    # url(r'^data/country/(?P<name>.+)$', views.DateCountry.as_view(), name='country'),



    url(r'sitemap\.xml$',
        cache_page(86400)(sitemap.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(r'sitemap-(?P<section>.+)-(?P<page>\d+)\.xml',
        cache_page(86400)(sitemap.sitemap),
        {'sitemaps': sitemaps}, name='sitemaps'),

    # url(r'search-data\.xml', search.index,),
    # url(r'search-data\.xml', search.search, name='search')
]
