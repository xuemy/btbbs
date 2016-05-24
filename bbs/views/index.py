#encoding:utf-8
from django.shortcuts import render

from bbs.models import Movie


def index(request):
    # types = Type.get_type_list()

    # 最新电影
    last_movie = Movie.objects.all()[:20]
    # 最新上映的电影
    last_show_movie = Movie.objects.exclude(torrent__isnull=True).exclude(show_time=None).filter(
        category__name='电影').order_by('-show_time').all()[:12]
    return render(request, 'index.html', {
        'last_movie': last_movie,
        'last_show_movie': last_show_movie,
        # 'hot_movie': hot_movie(request,display_amount=12),
        # 'hot_tv': hot_tv(request,display_amount=12)
    })