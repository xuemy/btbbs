# encoding:utf-8
from django.shortcuts import render
from django.views.generic import DetailView, ListView


def index(request):
    return render(request, "index.html")


class Detail(DetailView):pass
    # model = Movie
    # template_name = 'detail.html'
    # context_object_name = 'detail'
    #
    # def get_context_data(self, **kwargs):
    #     context = super(V, self).get_context_data(**kwargs)
    #     torrents = context['detail'].torrent_set.all()
    #     result = []
    #     for torrent in torrents:
    #         try:
    #             parse_torrent_detail = get_file_detail(json.loads(torrent.detail))
    #             parse_torrent_detail['obj'] = torrent
    #             result.append(parse_torrent_detail)
    #         except:
    #             continue
    #     context['torrents'] = result
    #     return context


class Tag(ListView):
    pass


class Genre(ListView):
    pass


class Data(ListView):
    pass


def download(request):
    return None
