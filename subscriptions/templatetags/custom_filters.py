from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Умножает value на arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Делит value на arg"""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, arg):
    """Процент value от arg"""
    try:
        return (float(value) / float(arg)) * 100 if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0