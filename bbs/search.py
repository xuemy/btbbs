#encoding:utf-8
from django.shortcuts import render

# from bbs.models import Movie_T
def index(request, search_data,
          template_name='sitemap_index.xml', content_type='application/xml',
          sitemap_url_name='django.contrib.sitemaps.views.sitemap',
          mimetype=None):
    pass


def search(request):
    data = None
    # data = Movie_T.objects.filter(subtype='movie').all()
    return render(request,'search.xml',{'data':data},content_type='application/xml')