import random
from io import BytesIO

from Blog.menu import DataMixin, menu
from PIL import Image
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import inlineformset_factory
from django.http import request, Http404, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.html import strip_tags
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormMixin, UpdateView, DeleteView, FormView
from slugify import slugify
from Blog.forms import CommentForm, AddPostForm, RegisterUserForm, LoginUserForm
from Blog.models import Posts, Category, CustomImage, Comments
from users.models import Profile


class HomePage(DataMixin, ListView):
    model = Posts
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    ordering = ['-time_create']  # order posts by date in descending order
    paginate_by = 5  # display 10 posts per page

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_published=True)  # only show published posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        posts = self.get_queryset()
        context['posts'] = posts
        c_def = self.get_user_context()
        return dict(list(context.items()) + list(c_def.items()))


class PostDetail(DataMixin, DetailView, FormMixin):
    model = Posts
    template_name = 'blog/post_detail.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'
    form_class = CommentForm
    success_msg = 'Коментарий создан'

    def get_success_url(self, **kwargs):
        return reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):  # проверка поля коментария
        self.object = form.save(commit=False)
        self.object.article = self.get_object()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # context['title'] = str(Posts.title)
    #     c_def = self.get_user_context(title='Страница поста')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post_images'] = post.post_images.all()
        context['title'] = 'Страница поста'
        c_def = self.get_user_context()
        return dict(list(context.items()) + list(c_def.items()))


class CategoryPosts(DataMixin, ListView):
    model = Posts
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        category_slug = self.kwargs['cat_slug']
        # Get the child category using the slug from the URL
        child_category = Category.objects.get(slug=category_slug)

        # If the selected category is a parent category, get all posts for its descendants
        if not child_category.is_leaf_node():
            return Posts.objects.filter(
                Q(cat_post__in=child_category.get_descendants(include_self=True)),
                is_published=True)

        # If the selected category is a leaf node (a child category), get posts for the specific category only
        return Posts.objects.filter(cat_post=child_category, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(c.name), cat_selected=c.pk)
        return dict(list(context.items()) + list(c_def.items()))


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
        print(main_category, new_category)

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
            # if main_category is not None and main_category.parent != category:
            if main_category is not None:
                # Установка основной категории в качестве родителя для новой категории
                category.parent = main_category
                category.save()
            else:
                # Вывод сообщения об ошибке
                messages.error(self.request, 'Новая категория не может быть потомком основной категории.')

            # Если есть основная категория, устанавливаем ее в качестве родительской для новой категории
            # category.parent = main_category

        try:
            obj.save()
            for file in files:
                CustomImage.objects.create(post=obj, image=file)

        except ValidationError as e:
            # если возникает ошибка уникальности поля, генерируем новый slug и пытаемся сохранить объект поста еще раз
            if 'slug' in e.error_dict:
                slug = f"{slug}-{random.randint(1, 1000)}"
                form.instance.slug = slug
                return self.form_valid(form)
            else:
                raise e

        return HttpResponseRedirect(reverse('home'))

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
    success_url = reverse_lazy('home')

    # Определите, какие поля требуется обработать в формсете изображений
    PostImageFormSet = inlineformset_factory(Posts, CustomImage, fields=('image',), extra=1)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user

        formset = self.PostImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        new_images = self.request.FILES.getlist('images')
        deleted_images_count = 0

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
                CustomImage.objects.create(post=post, image=file)

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
    return render(request, 'blog/contact.html', {'menu': user_menu, 'title': 'Контакты'})


# Отображение уведомлений
def show_notifications(request):
    profile = Profile.objects.get(user=request.user)
    notifications = profile.notifications.split('\n') if profile.notifications else []

    processed_notifications = []
    for notification in notifications:
        if "Пост" in notification:
            post_title = notification.split('"')[1]
            try:
                post = Posts.objects.get(title=post_title)
                post_link = str(post.get_absolute_url())
                processed_notifications.append((post_link, notification))
            except Posts.DoesNotExist:
                processed_notifications.append((None, notification))
        else:
            processed_notifications.append((None, notification))

    return render(request, 'blog/notifications.html', {'notifications': processed_notifications, 'menu': menu,})


def clear_notifications(request):
    profile = Profile.objects.get(user=request.user)
    profile.notifications = ''
    profile.save()
    return redirect('show_notifications')


# class RegisterUser(CreateView):
#     form_class = RegisterUserForm
#     template_name = 'blog/register.html'
#     success_url = reverse_lazy('home')
#
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         user = form.save()
#         login(self.request, user)
#         return response
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Регистрация'
#         return context
#
#
# class LoginUser(LoginView):
#     form_class = LoginUserForm
#     template_name = 'blog/login.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Авторизация'
#         return context
#
#     def get_success_url(self):
#         return reverse_lazy('home')
#
#
# def logout_user(request):
#     logout(request)
#     return redirect('login')
