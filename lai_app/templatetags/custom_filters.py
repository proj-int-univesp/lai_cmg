from django import template

register = template.Library()

@register.filter
def add_days(value, days):
    from datetime import timedelta
    return value + timedelta(days=int(days))