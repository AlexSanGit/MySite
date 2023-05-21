from Blog.forms import *
from Blog.models import Posts
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormMixin


class HomePage(ListView):
    model = Posts
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    ordering = ['-time_create']  # order posts by date in descending order
    paginate_by = 10  # display 10 posts per page

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_published=True)  # only show published posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context


class PostDetail(DetailView, FormMixin):
    model = Posts
    template_name = 'blog/post_detail.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'
    form_class = CommentForm
    success_msg = 'Коментарий создан'

    def get_success_url(self, **kwargs):
        return reverse_lazy('post:post_slug')

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
        context['title'] = 'Главная страница'
        return context


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'blog/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
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

