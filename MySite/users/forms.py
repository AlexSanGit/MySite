from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.html import format_html
from users.choices.city_choices import CITY_CHOICES
from users.models import Profile


class ImagePreviewClearableFileInput(forms.ClearableFileInput):
    def render(self, name, value, attrs=None, renderer=None):
        template = '<div class="custom-clearable-file-input">' \
                   '<label class="custom-clearable-file-input-label" for="{}">' \
                   '<img class="custom-clearable-file-input-preview" src="{}" alt="Фото">' \
                   '</label>' \
                   '<input type="{}" name="{}" class="custom-clearable-file-input-file" id="{}">' \
                   '<span class="custom-clearable-file-input-clear">' \
                   '</span>' \
                   '</div>'
        return format_html(template, attrs['id'], value.url if value else '', self.input_type, name, attrs['id'], attrs['id'])


class UserRegisterForm(UserCreationForm):
    # email = forms.EmailField()
    city = forms.ChoiceField(choices=CITY_CHOICES, label='Участок')
    welcome_code = forms.IntegerField(required=True, label="Код приглашения")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'city', 'welcome_code', 'first_name', 'last_name']

    def clean_welcome_code(self):
        welcome_code = self.cleaned_data['welcome_code']
        if welcome_code < 10000 or welcome_code > 99999:
            raise forms.ValidationError('Код приглашения должен содержать 5 цифр.')
        return welcome_code


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    city = forms.ChoiceField(choices=CITY_CHOICES, label='Участок')
    # is_seller = forms.BooleanField(label='Поставьте галочку если вы продавец', required=False)
    image = forms.ImageField(label='Фото', required=False, widget=ImagePreviewClearableFileInput(attrs={'accept': 'image/*'}))
    phone = forms.IntegerField(required=False, label="Сот.телефон")
    city_filter = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,  # Для отображения как чекбоксы
        choices=CITY_CHOICES,  # Ваш список городов
    )

    class Meta:
        model = Profile
        fields = ['city',  'phone', 'image', 'city_filter']


