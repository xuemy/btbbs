#encoding:utf-8
import json

from django.http import Http404
from django.shortcuts import get_object_or_404, render

from bbs.models import Torrent


def view(request, tid):
    etag = request.GET.get('etag')
    name = request.GET.get('name')
    torrent = get_object_or_404(Torrent, movie_id=tid, etag=etag)
    magnet = 'magnet:?xt=urn:btih:{}'.format(torrent.hash)
    try:
        detail = json.loads(torrent.detail)
        return render(request, "download.html", {'torrent': torrent, 'detail': detail, 'magnet': magnet})
    except:
        # torrent.delete()
        raise Http404()

# class D(DetailView):
#     model = Torrent
#     slug_field = 'movie_id'
#     slug_url_kwarg = 'movie_id'
#     query_pk_and_slug = True
#     template_name = 'download.html'
#     context_object_name = 'torrent'
#
#     def get_context_data(self, **kwargs):
#         context = super(D, self).get_context_data(**kwargs)
#         torrent = context['torrent']
#         magnet = 'magnet:?xt=urn:btih:{}'.format(torrent.hash)
#         context['magnet'] = magnet
#         return context
