#encoding:utf-8

from django.views.generic import ListView

from bbs.models import Movie


# from bbs.utils import pagination


# def tag(request, tag_name):
#     order = request.GET.get('order', "")
#     t = request.GET.get('type', '')
#
#     if order and string.lower(order) not in ['desc', 'asc']:
#         raise Http404()
#     if t and string.lower(t) not in ['pubdate', 'rating', 'year']:
#         raise Http404()
#
#     objects = Movie.objects.filter(tags__name=tag_name).order_by('-rating').all()
#
#     objs, page_range = pagination(request, objects)
#     return render(
#         request,
#         'tag.html',
#         {
#             'objs': objs,
#             'page_range': page_range,
#             'name': tag_name,
#         }
#     )

class Tag(ListView):
    template_name = 'tag.html'
    paginate_by = 20
    
    def get_queryset(self):
        return Movie.objects.filter(tags__name=self.kwargs['tag_name']).order_by('-rating').all()
    
    def get_context_data(self, **kwargs):
        context = super(Tag, self).get_context_data(**kwargs)
        range_page = list(context['paginator'].page_range)
        page = context['page_obj'].number
        all_number = context['paginator'].num_pages

        if all_number <= 9:
            context['page_range'] = range_page
        else:
            if page + 5 < 9:
                context['page_range'] = range_page[:page + 4] + ['...'] + range_page[-2:]
            else:
                # if page - 3 > 2 and page + 2 < all_number:
                context['page_range'] = [range_page[0]] + ['...'] + range_page[page - 3:page + 2] + ['...'] + range_page[-2:]
        return context

