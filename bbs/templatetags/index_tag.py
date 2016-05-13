#encoding:utf-8
import string

import six
from django import template

register = template.Library()

@register.filter('name_tag')
def name_tag(name):
    return string.split(name, maxsplit=1)[0]



if __name__ == '__main__':
    name_tag('蓝山球队大电影 Blue Mountain State: The Rise of Thadland')