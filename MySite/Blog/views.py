import os
import random
import re
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from Blog import models
from Blog.menu import DataMixin, menu
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import inlineformset_factory, modelform_factory
from django.http import HttpResponseRedirect, request
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormMixin, UpdateView, DeleteView, FormView
from slugify import slugify
from Blog.forms import CommentForm, AddPostForm, ContactForm
from Blog.models import Posts, Category, CustomImage, Comments
from users.models import Profile, User
from datetime import datetime
from django.db.models import Count  # Добавляем импорт Count
from .forms import AddPostForm
from .models import Category


class PostDetail(LoginRequiredMixin, DataMixin, DetailView, FormMixin):
    model = Posts
    template_name = 'blog/post_detail.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'
    form_class = CommentForm
    success_msg = 'Коментарий создан'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self, **kwargs):
        return reverse('post', kwargs={'post_slug': self.object.article.slug})

    def form_valid(self, form):  # проверка поля коментария
        self.object = form.save(commit=False)
        self.object.article = self.get_object()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        # Используйте filter() для получения записи с определенным slug
        return get_object_or_404(Posts, slug=self.kwargs['post_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post_images'] = post.post_images.all()
        context['title'] = 'Страница поста'
        # Получаем профиль пользователя текущего поста
        profile = User.objects.get(username=self.object.author).profile
        context['profile'] = profile
        c_def = self.get_user_context()
        return dict(list(context.items()) + list(c_def.items()))


class FilterMixin:
    def filter_by_city(self, queryset):
        if self.request.user.is_authenticated:
            profile = self.request.user.profile
            selected_cities = profile.city_filter.split(",") if profile.city_filter else []

            if selected_cities:
                city_filter_q = Q()
                for city in selected_cities:
                    city_filter_q |= Q(city=city)
                queryset = queryset.filter(city_filter_q)
        return queryset


class HomePage(LoginRequiredMixin, DataMixin, FilterMixin, ListView):
    model = Posts
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    ordering = ['-time_create']
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)
        queryset = self.filter_by_city(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        posts = self.get_queryset()
        context['posts'] = posts

        if self.request.user.is_authenticated:
            profile = self.request.user.profile
            context['profile'] = profile

        c_def = self.get_user_context()
        return dict(list(context.items()) + list(c_def.items()))


class CategoryPosts(LoginRequiredMixin, DataMixin, FilterMixin, ListView):
    model = Posts
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        category_slug = self.kwargs['cat_slug']
        child_category = Category.objects.get(slug=category_slug)

        if child_category.parent_id is None:
            queryset = Posts.objects.filter(
                Q(cat_post__parent_id=child_category.id) | Q(cat_post=child_category),
                is_published=True)
        else:
            queryset = Posts.objects.filter(cat_post=child_category, is_published=True)

        queryset = self.filter_by_city(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(c.name))
        return dict(list(context.items()) + list(c_def.items()))


def is_image(file):
    # Получите расширение файла
    _, file_extension = os.path.splitext(file.name)

    # Список поддерживаемых расширений изображений
    supported_image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']

    # Проверьте, является ли расширение поддерживаемым изображением
    return file_extension.lower() in supported_image_extensions


def resize_image(image):
    # Чтение данных из InMemoryUploadedFile
    image_data = image.read()

    # Открываем изображение с использованием Pillow
    pil_image = Image.open(BytesIO(image_data))

    # Устанавливаем максимальный размер изображения
    max_size = (800, 600)

    # Вычисляем соотношение сторон
    width, height = pil_image.size
    aspect_ratio = width / height

    # Если размер изображения превышает максимальный размер, изменяем его
    if width > max_size[0] or height > max_size[1]:
        if aspect_ratio > 1:
            new_width = max_size[0]
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = max_size[1]
            new_width = int(new_height * aspect_ratio)

        pil_image = pil_image.resize((new_width, new_height), Image.ANTIALIAS)

        # Создаем новый объект BytesIO для сохранения измененного изображения в памяти
        output_io = BytesIO()
        pil_image.save(output_io, format='JPEG', quality=100)  # Можете выбрать другой формат и качество, если нужно

        # Создаем новый InMemoryUploadedFile с измененными данными
        processed_image = InMemoryUploadedFile(
            output_io,
            None,
            f"{image.name.split('.')[0]}_processed.jpg",
            'image/jpeg',
            output_io.tell(),
            None
        )

        return processed_image
    else:
        # Если изображение не требует изменения, возвращаем оригинальное изображение
        return image


# def process_image_in_memory(image):
#     # Чтение данных из InMemoryUploadedFile
#     image_data = image.read()
#
#     # Открываем изображение с использованием Pillow
#     pil_image = Image.open(BytesIO(image_data))
#
#     # Устанавливаем максимальный размер изображения
#     max_size = (800, 600)
#
#     # Если размер изображения превышает максимальный размер, изменяем его
#     if pil_image.size[0] > max_size[0] or pil_image.size[1] > max_size[1]:
#         pil_image.thumbnail(max_size)
#
#         # Создаем новый объект BytesIO для сохранения измененного изображения в памяти
#         output_io = BytesIO()
#         pil_image.save(output_io, format='JPEG', quality=40)  # Можете выбрать другой формат и качество, если нужно
#
#         # Обновляем данные в InMemoryUploadedFile
#         image.file = output_io
#         # Устанавливаем имя файла, необходимое для InMemoryUploadedFile
#         image.file.name = f"{image.name.split('.')[0]}_processed.jpg"
#
#     return image


class AddPost(LoginRequiredMixin, DataMixin, CreateView, FormMixin):
    form_class = AddPostForm
    template_name = 'blog/addpage.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form, *args, **kwargs):
        obj = form.save(commit=False)
        obj.author = self.request.user
        # obj.save()
        # Получение списка файлов
        files = self.request.FILES.getlist('images')
        obj.city = form.cleaned_data['city']
        # Установите начальное значение для city_filter
        obj.time_zayavki = form.cleaned_data['time_zayavki']
        obj.time_glybinie = form.cleaned_data['time_glybinie']
        obj.time_end = form.cleaned_data['time_end']
        obj.ot_kogo_zayavka = form.cleaned_data['ot_kogo_zayavka']
        simulyation_value = form.cleaned_data.get('simulyation', False)
        form.instance.simulyation = simulyation_value
        # Получение второго пользователя из формы
        second_user = form.cleaned_data.get('second_user')
        if second_user:
            obj.second_user = second_user
        # создаем slug из заголовка поста с помощью функции slugify из библиотеки python-slugify
        slug = slugify(form.cleaned_data['title'])
        # проверяем уникальность slug
        if Posts.objects.filter(slug=slug).exists():
            # если slug уже занят, генерируем новый slug путем добавления случайного числа к оригинальному slug
            slug = f"{slug}-{random.randint(1, 1000)}"
        # добавляем slug в объект поста
        form.instance.slug = slug

        new_category = form.cleaned_data.get('new_category')
        main_category = form.cleaned_data.get('cat_post')
        # print(main_category, new_category)

        if new_category:
            # Получение объекта основной категории
            try:
                # Попытка получить уже существующую категорию с указанным именем
                category = Category.objects.get(name=new_category)
            except Category.DoesNotExist:
                # Если категория не существует, создаем новую
                slug = slugify(new_category)
                category = Category.objects.create(name=new_category, slug=slug)
                # Связываем пост с выбранной или созданной категорией
                obj.cat_post = category

            # Проверка, что новая категория не является родителем основной категории
            if new_category and main_category is not None:
                if category.is_descendant_of(main_category):
                    messages.error(self.request, 'Новая категория не может быть потомком основной категории.')
                else:
                    try:
                        category.parent = main_category
                        category.save()
                    except Exception as e:
                        # Обработка возможных ошибок при установке родителя
                        messages.error(self.request, 'Ошибка при установке родителя для новой категории.')

            else:
                # Вывод сообщения об ошибке
                messages.error(self.request, 'Новая категория не может быть потомком основной категории.')

        try:
            obj.save()
            # Обработка изображений
            # for file in files:
            #     try:
            #         processed_image = process_image_in_memory(file)
            #         if is_image(processed_image):
            #             # Теперь вы можете использовать processed_image для сохранения в модели или другом месте
            #             CustomImage.objects.create(post=obj, image=processed_image)
            #         else:
            #             # Обработка случая, если это не изображение
            #             continue
            #     except Exception as e:
            #         # Обработка других исключений, если необходимо
            #         messages.error(self.request, f'Файл {file.name} не изображение')
            for file in files:
                try:
                    # print(f"Обработка файла: {file.name}")
                    processed_image = resize_image(file)
                    if processed_image:
                        # print(f"Файл {file.name} обработан успешно")
                        # Теперь вы можете использовать processed_image для сохранения в модели или другом месте
                        CustomImage.objects.create(post=obj, image=processed_image)
                    else:
                        # Обработка случая, если это не изображение
                        messages.error(self.request, f'Файл {file.name} не изображение')
                        continue
                except Exception as e:
                    # Обработка других исключений, если необходимо
                    # print(f"Ошибка при обработке файла {file.name}: {e}")
                    messages.error(self.request, f'Файл {file.name} не изображение')

        except ValidationError as e:
            print(e)
            # если возникает ошибка уникальности поля, генерируем новый slug и пытаемся сохранить объект поста еще раз
            if 'slug' in e.error_dict:
                slug = f"{slug}-{random.randint(1, 1000)}"
                form.instance.slug = slug
                return self.form_valid(form)
            else:
                raise e

        # Получить время из объекта time_glybinie
        post_time_glybinie = obj.time_glybinie

        # Получить текущее время из профиля пользователя
        current_time_glybinie = self.request.user.profile.time_glybinie

        # Выполнить операции с часами и минутами
        new_hours = current_time_glybinie.hour + post_time_glybinie.hour
        new_minutes = current_time_glybinie.minute + post_time_glybinie.minute

        # Проверить, если минуты превысили 60, скорректировать часы и минуты
        if new_minutes >= 60:
            new_hours += new_minutes // 60
            new_minutes = new_minutes % 60

        # Создать новую строку времени в формате "часы:минуты"
        updated_time_glybinie = f"{new_hours:02}:{new_minutes:02}"

        # Если текущий день месяца равен 1, обнулите поле glubinie
        # Получите текущую дату и время
        now = datetime.now()
        if now.day == 1 and now.hour > 12:
            zero_time_glybinie = f"{00:02}:{00:02}"
            # Получите всех пользователей и обнулите поле glubinie для их профилей
            users = User.objects.all()
            for user in users:
                user.profile.time_glybinie = zero_time_glybinie
                user.profile.save()
        else:
            # Обновить значение в профиле пользователя
            self.request.user.profile.time_glybinie = updated_time_glybinie
            self.request.user.profile.save()

        return HttpResponseRedirect(reverse('home'))

    def get_initial(self):
        initial = super().get_initial()
        # Получаем наиболее используемую категорию
        most_used_category = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count').first()
        initial['cat_post'] = most_used_category
        # Получаем профиль пользователя
        profile = self.request.user.profile if self.request.user.is_authenticated else None
        if profile:
            # Получаем список выбранных участков (городов) из профиля пользователя
            selected_cities = profile.city_filter.split(',') if profile.city_filter else []
            # Если есть выбранные участки, устанавливаем первый в качестве начального значения
            if selected_cities:
                initial['city'] = selected_cities[0]

        return initial

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Добавить запись")
        return dict(list(context.items()) + list(c_def.items()))


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Posts
    queryset = Posts.objects.all()  # или определите свой запрос для получения объектов
    form_class = AddPostForm
    template_name = 'blog/edit_posts_form.html'
    # fields = ['title', 'description', 'cat_post', 'images']
    # Определите, какие поля требуется обработать в формсете изображений
    PostImageFormSet = inlineformset_factory(Posts, CustomImage, fields=('image',), extra=1)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        formset = self.PostImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        new_images = self.request.FILES.getlist('images')
        deleted_images_count = 0

        # Получаем значения времени из POST-запроса
        time_zayavki = self.request.POST.get('time_zayavki')
        time_glybinie = self.request.POST.get('time_glybinie')

        simulyation_value = form.cleaned_data['simulyation']
        post.simulyation = simulyation_value
        # second_user = self.request.POST.get('second_user')
        second_user = form.cleaned_data['second_user']
        post.second_user = second_user

        # Присваиваем значения времени посту
        post.time_zayavki = time_zayavki
        post.time_glybinie = time_glybinie

        # Обработайте удаление изображений
        for image in self.object.post_images.all():
            delete_field_name = f"delete_image_{image.id}"
            if self.request.POST.get(delete_field_name) == "True":
                image.delete()
                deleted_images_count += 1

        existing_images_count = len(self.object.post_images.all()) - deleted_images_count
        total_images_count = existing_images_count + len(new_images)

        if total_images_count > 3:
            messages.error(self.request, 'Максимальное количество изображений - 3.')
            return self.form_invalid(form)
        else:
            # Обработайте формсет изображений
            if formset.is_valid():
                formset.save()

            # Создание новых изображений
            for file in new_images:

                try:
                    processed_image = process_image_in_memory(file)
                    if is_image(processed_image):

                        # Теперь вы можете использовать processed_image для сохранения в модели или другом месте
                        CustomImage.objects.create(post=post, image=processed_image)
                    else:
                        # Обработка случая, если это не изображение
                        continue
                except Exception as e:
                    # Обработка других исключений, если необходимо
                    messages.error(self.request, f'Файл {file.name} не изображение')

        post.save()
        messages.success(self.request, 'Пост успешно обновлен.')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_images'] = self.object.post_images.all()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # При редактировании поста устанавливаем начальное значение для поля времени
        if self.object:
            form.fields['time_zayavki'].initial = self.object.time_zayavki
            form.fields['time_glybinie'].initial = self.object.time_glybinie

        # При редактировании поста удаляем поле "Новая категория"
        if self.object:
            del form.fields['new_category']

        return form

    def get_success_url(self):
        return reverse_lazy('post', kwargs={'post_slug': self.object.slug})  # Замените на имя вашего маршрута


class PostsSimulyationView(DataMixin, ListView):
    model = Posts
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Posts.objects.filter(simulyation=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Симуляции")
        return dict(list(context.items()) + list(c_def.items()))


class PostsImportantView(DataMixin, ListView):
    model = Posts
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Posts.objects.filter(important=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Важные записи")
        return dict(list(context.items()) + list(c_def.items()))


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Posts
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('home')
    # slug_url_kwarg = 'slug'
    context_object_name = 'post'
    success_msg = 'Коментарий создан'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Пост успешно удален.')
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


def comment_detail_view(request, pk):
    comment = get_object_or_404(Comments, pk=pk)
    # Ваша логика для отображения деталей комментария здесь
    # Например, вы можете отобразить шаблон с деталями комментария
    return render(request, 'comment_detail.html', {'comment': comment})


def about(request):
    user_menu = menu.copy()
    if not request.user.is_authenticated:
        user_menu.pop(1)  # Индекс элемента "Добавить запись" в списке меню
    return render(request, 'blog/about.html', {'menu': user_menu, 'title': 'О сайте'})


def contact(request):
    user_menu = menu.copy()
    if not request.user.is_authenticated:
        user_menu.pop(1)  # Индекс элемента "Добавить запись" в списке меню

    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Обработайте отправку сообщения, например, отправьте его на почту администратора
            # Добавьте код отправки почты или любую другую логику обработки сообщения
            # ...

            return render(request, 'blog/email/contact_success.html')  # Страница успешной отправки

    # return render(request, 'contact.html', {'form': form})
    return render(request, 'blog/contact.html', {'form': form, 'menu': user_menu, 'title': 'Контакты'})


def show_notifications(request):
    profile = Profile.objects.get(user=request.user)
    notifications = profile.notifications.split('\n') if profile.notifications else []

    # Создайте новый список уведомлений, исключая те, связанные с несуществующими постами
    processed_notifications = []
    for notification in notifications:
        if "Пост" in notification:
            # Ищем ссылку на пост с помощью регулярного выражения
            match = re.search(r'Нажмите чтобы перейти: (.*?)$', notification)
            if match:
                post_link = match.group(1).strip()
                post_slug = post_link.split('/')[-2]  # Извлекаем slug из post_link
                try:
                    post = Posts.objects.get(slug=post_slug)
                    post_link = str(post.get_absolute_url())
                    processed_notifications.append((post_link, notification))
                except Posts.DoesNotExist:
                    # Если пост не существует, удаляем уведомление из профиля пользователя
                    continue
        else:
            processed_notifications.append((None, notification))

    # Обновите уведомления в профиле пользователя
    profile.notifications = '\n'.join([notification[1] for notification in processed_notifications])
    profile.save()

    return render(request, 'blog/notifications.html', {'notifications': processed_notifications, 'menu': menu})


def clear_notifications(request):
    profile = Profile.objects.get(user=request.user)
    profile.notifications = ''
    profile.save()
    return redirect('home')


class UserListView(DataMixin, ListView):
    model = User  # Используйте свою модель пользователя, если она отличается
    template_name = 'blog/user_list.html'  # Создайте соответствующий шаблон
    context_object_name = 'users'
    paginate_by = None  # Отключаем пагинацию

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем статистику о количестве постов для каждого пользователя
        users_post_count = User.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')
        context['users_post_count'] = users_post_count
        context['profiles'] = Profile.objects.all().order_by('city')
        c_def = self.get_user_context()
        return dict(list(context.items()) + list(c_def.items()))


def welcome(request):
    return render(request, 'blog/welcome.html')
