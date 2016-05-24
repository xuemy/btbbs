#encoding:utf-8

from django import template
from w3lib.html import remove_tags
register = template.Library()

register.tag('remove_tags',remove_tags)

