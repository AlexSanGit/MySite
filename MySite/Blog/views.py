import random

from PIL import Image
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, request, Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormMixin, UpdateView, DeleteView
from slugify import slugify

from Blog.forms import CommentForm, AddPostForm, RegisterUserForm, LoginUserForm
from Blog.models import Posts, Category
from Blog.utils import DataMixin, menu


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

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.article = self.get_object()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['title'] = str(Posts.title)
        c_def = self.get_user_context(title='Страница поста')
        return dict(list(context.items()) + list(c_def.items()))


class CategoryPosts(DataMixin, ListView):
    model = Posts
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Posts.objects.filter(cat_post__slug=self.kwargs['cat_slug'], is_published=True)\
            .select_related('cat_post')

    def get_context_data(self, *, object_list=None, **kwargs):
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

        # user_profile = request.user.profile  # Получаем профиль пользователя
        # post = Post(title=title, content=content, city=user_profile)

        # создаем slug из заголовка поста с помощью функции slugify из библиотеки python-slugify
        slug = slugify(form.cleaned_data['title'])
        # проверяем уникальность slug
        if Posts.objects.filter(slug=slug).exists():
            # если slug уже занят, генерируем новый slug путем добавления случайного числа к оригинальному slug
            slug = f"{slug}-{random.randint(1, 1000)}"
        # добавляем slug в объект поста
        form.instance.slug = slug
        try:
            # вызываем метод родительского класса для сохранения объекта поста
            response = super().form_valid(form)
        except ValidationError as e:
            # если возникает ошибка уникальности поля, генерируем новый slug и пытаемся сохранить объект поста еще раз
            if 'slug' in e.error_dict:
                slug = f"{slug}-{random.randint(1, 1000)}"
                form.instance.slug = slug
                response = super().form_valid(form)
            else:
                raise e
        return response
        # obj.save()
        return response

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Начнем поиск")
        return dict(list(context.items()) + list(c_def.items()))


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Posts
    template_name = 'blog/edit_posts_form.html'
    fields = ['title', 'description', 'cat_post', 'photo_part']
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.author != self.request.user:
            raise Http404("You are not allowed to edit this post.")
        return obj

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
        # post = form.save(commit=False)
        # # if 'photo_part' in form.changed_data:
        # #     # Получаем изображение из формы
        # image = form.cleaned_data.get('photo_part')
        # # Открываем изображение с помощью библиотеки Pillow
        # img = Image.open(image)
        # # Меняем размер изображения
        # output_size = (500, 500)
        # img.thumbnail(output_size)
        # # Удаляем старое изображение
        # # if post.photo_part:
        # #     post.photo_part.delete()
        # # Сохраняем новое изображение
        # post.photo_part.save(image.name, img.format)
        # return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Posts
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'blog/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'blog/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')


def about(request):
    return render(request, 'blog/about.html', {'menu': menu, 'title': 'О сайте'})


def contact(request):
    return render(request, 'blog/contact.html', {'menu': menu, 'title': 'Контакты'})


# class UserDetail(LoginRequiredMixin, DataMixin, DetailView):
#     template_name = 'blog/user_detail.html'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         c_def = self.get_user_context(title="Профиль")
#         return dict(list(context.items()) + list(c_def.items()))

# def user_detail(request, user_id):
#     user = get_object_or_404(User, id=user_id)
#     profile = get_object_or_404(UserProfile, user=user)
#     context = {'user': user, 'profile': profile, 'menu': menu}
#     return render(request, 'blog/user_detail.html', context)


