from Blog.models import Category
from django import template

# здесь создаем тэги , для того чтобы обращаться с файлов шаблонов к ним

register = template.Library()


@register.inclusion_tag('blog/list_categories.html')
def show_categories(sort=None, cat_selected=0):
    if not sort:
        top_categories = Category.objects.filter(parent__isnull=True)
    else:
        top_categories = Category.objects.filter(parent__isnull=True).order_by(sort)

    def get_child_categories(category):
        child_categories = category.children.all()
        for child_category in child_categories:
            child_category.child_categories = get_child_categories(child_category)
        return child_categories

    for category in top_categories:
        category.child_categories = get_child_categories(category)

    return {"cats": top_categories, "cat_selected": cat_selected}


@register.inclusion_tag('blog/main-menu.html')
def show_menu():
    print('')




