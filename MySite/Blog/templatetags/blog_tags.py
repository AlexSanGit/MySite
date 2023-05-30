import profile

from django import template
from Blog.models import Category, UserProfile

# здесь создаем тэги , для того чтобы обращаться с файлов шаблонов к ним

register = template.Library()


@register.simple_tag(name='getcats')
def get_categories(filter=None):
    if not filter:
        return Category.objects.all()
    else:
        return Category.objects.filter(pk=filter)


@register.inclusion_tag('blog/list_categories.html')
def show_categories(sort=None, cat_selected=0):
    if not sort:
        cats = Category.objects.all()
    else:
        cats = Category.objects.order_by(sort)

    return {"cats": cats, "cat_selected": cat_selected}


@register.simple_tag()
def get_status_user():
    if UserProfile.is_seller is True:
        return 'Продавец'
    else:
        return 'Покупатель'
