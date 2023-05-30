from Blog.models import Category


menu = [{'title': "О сайте", 'url_name': 'about'},
        {'title': "Найти запчасть", 'url_name': 'add_page'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        # {'title': "Профиль", 'url_name': 'user_detail/1'},
]


class DataMixin:
    paginate_by = 5

    def get_user_context(self, **kwargs):
        context = kwargs
        cats = Category.objects.all()     #annotate(Count('partcar'))

        user_menu = menu.copy()
        if not self.request.user.is_authenticated:      # если не авторизован то убрать из меню строку 1
            user_menu.pop(1)

        context['menu'] = user_menu
        context['cats'] = cats

        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context


