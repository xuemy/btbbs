#encoding:utf-8
from __future__ import  unicode_literals

import json

from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404

from bbs.models import Movie, Torrent
from bbs.utils import humanbytes, get_torrent_film, get_file_detail


def index(request):
    # types = Type.get_type_list()

    return render(request,'index.html',)


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