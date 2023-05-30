from Blog.models import Comments, Posts
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.http import request


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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'width': 20, 'rows': 5})
        }


class AddPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat_post'].empty_label = "Категория не выбрана"
        self.fields['title'].label = "Заголовок"
        self.fields['description'].label = "Описание"
        self.fields['photo_part'].label = "Изображение"
        self.fields['is_published'].label = "Опубликовать? "
        # self.fields['author']

    class Meta:
        model = Posts
        fields = ['title', 'description', 'photo_part', 'is_published', 'cat_post']
        # title = forms.CharField(label='Заголовок', widget=forms.TextInput(attrs={'class': 'form-input'}))
        widgets = {
            'title': forms.TextInput(attrs={'cols': 60}),
            'description': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise ValidationError('Длина превышает 200 символов')
        return title
