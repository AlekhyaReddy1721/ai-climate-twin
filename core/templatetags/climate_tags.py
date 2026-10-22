from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter: {{ "a,b,c"|split:"," }}"""
    return [v.strip() for v in value.split(delimiter)]
