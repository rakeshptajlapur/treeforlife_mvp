from django import template

register = template.Library()

@register.filter
def percentage(value, max_value):
    try:
        return (float(value) / float(max_value)) * 100
    except (ValueError, ZeroDivisionError):
        return 0