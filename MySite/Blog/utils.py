import io
from PIL import Image
from Blog.models import Category


menu = [{'title': "Добавить запись", 'url_name': 'add_page'},
        {'title': "О сайте", 'url_name': 'about'},
        {'title': "Обратная связь", 'url_name': 'contact'},
        # {'title': "Профиль", 'url_name': 'user_detail/1'},
        ]


class DataMixin:
    paginate_by = 5

    def get_user_context(self, **kwargs):
        context = kwargs
        cats = Category.objects.all()  # annotate(Count('partcar'))

        user_menu = menu.copy()
        if not self.request.user.is_authenticated:  # если не авторизован то убрать из меню строку 1
            user_menu.pop(1)

        context['menu'] = user_menu
        context['cats'] = cats

        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context


class AvatarProcessor:
    def __init__(self, instance):
        self.instance = instance

    def process(self):
        if not self.instance.avatar:
            return
        # Определяем путь к файлу изображения
        image_path = self.instance.avatar.path
        # Определяем размеры изображения
        width, height = self.get_image_size(image_path)
        # Если размеры превышают заданный порог, уменьшаем изображение
        if width > 500 or height > 500:
            self.resize_image(image_path)

    def get_image_size(self, image_path):
        with open(image_path, 'rb') as f:
            data = f.read()
        width, height = Image.open(io.BytesIO(data)).size
        return width, height

    def resize_image(self, image_path):
        from PIL import Image
        # Открываем изображение
        image = Image.open(image_path)
        # Уменьшаем размеры изображения
        image.thumbnail((500, 500))
        # Сохраняем измененное изображение
        image.save(image_path)
