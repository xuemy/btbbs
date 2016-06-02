# encoding:utf-8
import json

from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView

from bbs.models import Movie, Torrent

class PaginationListView(ListView):
    paginate_by = 30
    context_object_name = 'article_list'

    def get_context_data(self, **kwargs):
        context = super(PaginationListView, self).get_context_data(**kwargs)

        page = context['page_obj'].number
        total_pages = context['paginator'].num_pages

        inner_window = 2
        outer_window = 1
        pages = []
        if total_pages < 2 * inner_window - 1:
            context['pages'] = range(1, total_pages + 1)
            return context

        win_from = page - inner_window
        win_to = page + inner_window
        if win_to > total_pages:
            win_from -= win_to - total_pages
            win_to = total_pages

        if win_from < 1:
            win_to = win_to + 1 - win_from
            win_from = 1
            if win_to > total_pages:
                win_to = total_pages

        if win_from > inner_window:
            pages.extend(range(1, outer_window + 1 + 1))
            pages.append(None)
        else:
            pages.extend(range(1, win_to + 1))

        if win_to < total_pages - inner_window + 1:
            if win_from > inner_window:
                pages.extend(range(win_from, win_to + 1))

            pages.append(None)
            pages.extend(range(total_pages - 1, total_pages + 1))
        elif win_from > inner_window:
            pages.extend(range(win_from, total_pages + 1))
        else:
            pages.extend(range(win_to + 1, total_pages + 1))

        context['pages'] = pages
        context['current_page'] = page
        return context


class Index(PaginationListView):
    template_name = 'bbs/index.html'

    def get_queryset(self):
        return Movie.objects.filter(pubdate__isnull=False).order_by('-pubdate')


class Detail(DetailView):
    model = Movie
    template_name = 'bbs/detail.html'
    context_object_name = 'detail'
    slug_url_kwarg = 'douban_id'
    slug_field = 'douban_id'
    query_pk_and_slug = True


class Tag(PaginationListView):
    template_name = "bbs/tag.html"
    def get_queryset(self):
        return Movie.objects.filter(tags__name__in=[self.kwargs['tag_name']]).order_by('-pubdate').all()


class Data(ListView):
    pass


def download(request, tid):
    etag = request.GET['etag']
    info_hash = request.GET['key']
    torrent = get_object_or_404(Torrent, pk=tid, etag=etag, info_hash=info_hash)

    return render(request, 'bbs/download.html', {'torrent': torrent})
