#encoding:utf-8
from __future__ import  unicode_literals

import json

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404

from bbs.models import Movie, Torrent, Category
from bbs.utils import humanbytes, get_torrent_film, get_file_detail


def index(request):
    # types = Type.get_type_list()

    # 最新电影
    last_movie = Movie.objects.all()[:20]
    # 最新上映的电影
    last_show_movie = Movie.objects.exclude(torrent__isnull=True).exclude(show_time=None).filter(category__name='电视剧').order_by('-show_time').all()[:12]
    return render(request,'index.html', {
        'last_movie': last_movie,
        'last_show_movie':last_show_movie,
    })


def thread(request):
    return None


def category(request):
    return None


def _torrent(torrents):

    result = []
    for t in torrents:
        d = json.loads(t.detail)
        d = get_torrent_film(d)
        total = sum(map(lambda x: x['size'], d))
        t.detail = sorted(
            map(lambda x: {'name': x['name'], 'size': humanbytes(x['size']), 'o_size': x['size']}, d),
            key=lambda y: y['o_size'],
            reverse=True
        )
        result.append(
            (humanbytes(total), t)
        )
    return result



def detail(request, tid):
    d = get_object_or_404(Movie, pk=tid)
    torrents = d.torrent_set.all()
    result = []
    for torrent in torrents:
        try:
            parse_torrent_detail = get_file_detail(json.loads(torrent.detail))
            parse_torrent_detail['obj'] = torrent
            result.append(parse_torrent_detail)
        except:
            continue


    return render(request, 'detail.html', {'detail':d,'torrents':result})


def download(request, tid):
    etag = request.GET.get('etag')
    name = request.GET.get('name')
    torrent = get_object_or_404(Torrent, movie_id=tid, etag = etag)
    magnet = 'magnet:?xt=urn:btih:{}'.format(torrent.hash)
    try:
        detail = json.loads(torrent.detail)
        return render(request, "download.html", {'torrent': torrent, 'detail':detail, 'magnet':magnet})
    except:
        torrent.delete()
        raise Http404()


def tag(request):
    return None