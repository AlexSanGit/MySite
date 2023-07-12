from django.urls import reverse_lazy
from django.views.generic import CreateView

from Blog.models import Comments, Posts, Category
from .widgets import MultipleFileInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.http import request
from multiupload.fields import MultiFileField


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class AddPostForm(forms.ModelForm):
    new_category = forms.CharField(label='Новая категория', max_length=100, required=False)
    images = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat_post'].empty_label = "Категория не выбрана"
        self.fields['title'].label = "Заголовок"
        self.fields['description'].label = "Описание"
        self.fields['images'].label = "Изображение"

    class Meta:
        model = Posts
        fields = ['title', 'description', 'images', 'cat_post', 'new_category']
        widgets = {
            'title': forms.TextInput(attrs={'cols': 60}),
            'description': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cat_post = cleaned_data.get('cat_post')
        new_category = cleaned_data.get('new_category')

        if not cat_post and not new_category:
            raise forms.ValidationError('Выберите категорию или введите новую')

        if new_category:
            # Проверка уникальности имени категории
            if Category.objects.filter(name=new_category).exists():
                raise forms.ValidationError('Категория с таким именем уже существует.')

# class AddPostView(CreateView):
#     model = Posts
#     form_class = AddPostForm
#     template_name = 'blog/add_post.html'
#     success_url = reverse_lazy('home')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'width': 20, 'rows': 5})
        }


# class AddPostForm(forms.ModelForm):
#     images = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5)
#     # images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['cat_post'].empty_label = "Категория не выбрана"
#         self.fields['title'].label = "Заголовок"
#         self.fields['description'].label = "Описание"
#         self.fields['images'].label = "Изображение"
#         # self.fields['is_published'].label = "Опубликовать? "
#
#     class Meta:
#         model = Posts
#         fields = ['title', 'description', 'images', 'cat_post']
#         # title = forms.CharField(label='Заголовок', widget=forms.TextInput(attrs={'class': 'form-input'}))
#         widgets = {
#             'title': forms.TextInput(attrs={'cols': 60}),
#             'description': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
#             # 'images': forms.ClearableFileInput(attrs={'multiple': True}),
#         }
#
#     def clean_title(self):
#         title = self.cleaned_data['title']
#         if len(title) > 100:
#             raise ValidationError('Длина превышает 200 символов')
#         return title
