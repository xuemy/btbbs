#encoding:utf-8
import json

from django.views.generic import DetailView

from bbs.models import Movie
from bbs.utils import get_file_detail



class V(DetailView):
    model = Movie
    template_name = 'detail.html'
    context_object_name = 'detail'

    def get_context_data(self, **kwargs):
        context = super(V, self).get_context_data(**kwargs)
        torrents = context['detail'].torrent_set.all()
        result = []
        for torrent in torrents:
            try:
                parse_torrent_detail = get_file_detail(json.loads(torrent.detail))
                parse_torrent_detail['obj'] = torrent
                result.append(parse_torrent_detail)
            except:
                continue
        context['torrents'] = result
        return context
