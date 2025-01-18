from django import template

register = template.Library()

@register.filter
def add_class(value, arg):
    """Adds a CSS class to the form field."""
    return value.as_widget(attrs={'class': arg})
