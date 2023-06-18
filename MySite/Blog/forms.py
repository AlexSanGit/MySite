from Blog.models import Comments, Posts
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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'width': 20, 'rows': 5})
        }


class AddPostForm(forms.ModelForm):
    # images = forms.ImageField(widget=forms.ClearableFileMultipleInput)
    images = MultiFileField(min_num=1, max_num=10, max_file_size=1024 * 1024 * 5)  # Пример настроек, можно изменить по своему усмотрению
    # images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat_post'].empty_label = "Категория не выбрана"
        self.fields['title'].label = "Заголовок"
        self.fields['description'].label = "Описание"
        self.fields['photo_part'].label = "Изображение"
        self.fields['is_published'].label = "Опубликовать? "

    class Meta:
        model = Posts
        fields = ['title', 'description', 'photo_part', 'images', 'is_published', 'cat_post']
        # title = forms.CharField(label='Заголовок', widget=forms.TextInput(attrs={'class': 'form-input'}))
        widgets = {
            'title': forms.TextInput(attrs={'cols': 60}),
            'description': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
            # 'images': forms.ClearableFileMultipleInput(attrs={'multiple': True}),
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 100:
            raise ValidationError('Длина превышает 200 символов')
        return title


# class ProfileForm(UserCreationForm):
#     username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
#     is_seller = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
#     rating = forms.IntegerField()
#     review = forms.TextField()
#     email = forms.EmailField()
#     password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
#     avatar = forms.ImageField()
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'rating', 'review', 'avatar')