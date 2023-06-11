from django import template

register = template.Library()


@register.filter
def message_with_animation(message):
    return message
