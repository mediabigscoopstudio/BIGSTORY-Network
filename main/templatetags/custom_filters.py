from django import template
from django.utils.html import strip_tags

register = template.Library()

@register.filter
def word_count(value):
    if not value:
        return 0
    return len(strip_tags(value).split())