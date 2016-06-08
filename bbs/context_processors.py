#encoding:utf-8
from django.conf import settings
from django.contrib.sites.models import Site


def setting(name, default=None):
    """
    Helper function to get a Django setting by name or (optionally) return
    a default (or else ``None``).
    """
    return getattr(settings, name, default)

def site(request):
    return {
        'site': Site.objects.get(id=settings.SITE_ID),
        'default_genres': [
            '动作',
            '战争',
            '爱情',
            '奇幻',
            '冒险',
            '科幻',
            '恐怖',
            '记录',
            '剧情',
            '历史',
            '武侠',
            '灾难',
            '悬疑',
        ],

    }