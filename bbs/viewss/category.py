#encoding:utf-8

from bbs.views.tag import Tag

from bbs.models import Movie, Category as Cat


class Category(Tag):
    CATEGORY = {
        'movie': '电影',
        'tv': '电视剧'
    }
    template_name = 'category.html'

    def get_queryset(self):
        c = Cat.objects.get(name=self.CATEGORY[self.kwargs['category']])
        return Movie.objects.exclude(torrent__isnull=True).exclude(show_time=None). \
               filter(category = c).order_by('-show_time').all()