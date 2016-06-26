# encoding:utf-8
import warnings

import six
from django.contrib.sitemaps.views import x_robots_tag
from django.contrib.sites.shortcuts import get_current_site
from django.core import urlresolvers
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.response import TemplateResponse


def _index(template_name='sitemap_index.xml'):
    @x_robots_tag
    def index(request, sitemaps,
              template_name=template_name, content_type='application/xml',
              sitemap_url_name='django.contrib.sitemaps.views.sitemap',
              mimetype=None):
        if mimetype:
            warnings.warn("The mimetype keyword argument is deprecated, use "
                          "content_type instead", DeprecationWarning, stacklevel=2)
            content_type = mimetype

        req_protocol = 'https' if request.is_secure() else 'http'
        req_site = get_current_site(request)

        sites = []
        for section, site in sitemaps.items():
            if callable(site):
                site = site()
            protocol = req_protocol if site.protocol is None else site.protocol
            for page in range(1, site.paginator.num_pages + 1):
                sitemap_url = urlresolvers.reverse(
                    sitemap_url_name, kwargs={'section': section, 'page': page})
                absolute_url = '%s://%s%s' % (protocol, req_site.domain, sitemap_url)
                sites.append(absolute_url)

        return TemplateResponse(request, template_name, {'sitemaps': sites},
                                content_type=content_type)

    return index


def _sitemap(tempalte_name='sitemap.xml'):
    @x_robots_tag
    def sitemap(request, sitemaps, section=None, page=1,
                template_name=tempalte_name, content_type='application/xml',
                mimetype=None):
        if mimetype:
            warnings.warn("The mimetype keyword argument is deprecated, use "
                          "content_type instead", DeprecationWarning, stacklevel=2)
            content_type = mimetype

        req_protocol = 'https' if request.is_secure() else 'http'
        req_site = get_current_site(request)

        if section is not None:
            if section not in sitemaps:
                raise Http404("No sitemap available for section: %r" % section)
            maps = [sitemaps[section]]
        else:
            maps = list(six.itervalues(sitemaps))

        urls = []
        for site in maps:
            try:
                if callable(site):
                    site = site()
                urls.extend(site.get_urls(page=page, site=req_site,
                                          protocol=req_protocol))
            except EmptyPage:
                raise Http404("Page %s empty" % page)
            except PageNotAnInteger:
                raise Http404("No page '%s'" % page)
        return TemplateResponse(request, template_name, {'urlset': urls},
                                content_type=content_type)

    return sitemap


# @x_robots_tag
# def index(request, sitemaps,
#           template_name='sitemap_index.xml', content_type='application/xml',
#           sitemap_url_name='django.contrib.sitemaps.views.sitemap',
#           mimetype=None):
#     if mimetype:
#         warnings.warn("The mimetype keyword argument is deprecated, use "
#                       "content_type instead", DeprecationWarning, stacklevel=2)
#         content_type = mimetype
#
#     req_protocol = 'https' if request.is_secure() else 'http'
#     req_site = get_current_site(request)
#
#     sites = []
#     for section, site in sitemaps.items():
#         if callable(site):
#             site = site()
#         protocol = req_protocol if site.protocol is None else site.protocol
#         for page in range(1, site.paginator.num_pages + 1):
#             sitemap_url = urlresolvers.reverse(
#                 sitemap_url_name, kwargs={'section': section, 'page': page})
#             absolute_url = '%s://%s%s' % (protocol, req_site.domain, sitemap_url)
#             sites.append(absolute_url)
#
#     return TemplateResponse(request, template_name, {'sitemaps': sites},
#                             content_type=content_type)
index = _index()
sitemap = _sitemap()

search_index = _index()


# search_sitemap = _sitemap(tempalte_name='bbs/search_sitemap.xml')

@x_robots_tag
def search_sitemap(request, sitemaps, section=None, page=1,
                   template_name='bbs/search_sitemap.xml', content_type='application/xml',
                   mimetype=None):
    if mimetype:
        warnings.warn("The mimetype keyword argument is deprecated, use "
                      "content_type instead", DeprecationWarning, stacklevel=2)
        content_type = mimetype

    req_protocol = 'https' if request.is_secure() else 'http'
    req_site = get_current_site(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = list(six.itervalues(sitemaps))

    urls = []
    for site in maps:
        try:
            if callable(site):
                site = site()
            urls.extend(site.items())
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    return TemplateResponse(request, template_name, {'urlset': urls},
                            content_type=content_type)
