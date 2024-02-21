from Blog.models import Comments, Posts, Category
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
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
    new_category = forms.CharField(label='Добавить новое оборудование', max_length=40, required=False)
    images = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5, required=False)
    ot_kogo_zayavka = forms.CharField(required=False)
    second_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='Совместно с ..'
       )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time_zayavki'].initial = '00:00'
        self.fields['time_glybinie'].initial = '00:00'
        self.fields['time_end'].initial = '00:00'
        self.fields['second_user'].empty_label = "Не выбрано"
        self.fields['second_user'].label_from_instance = self.label_from_instance
        self.fields['city'].initial = 'asu'
        self.fields['cat_post'].empty_label = "Категория не выбрана"
        self.fields['title'].label = "Краткое описание"
        self.fields['ot_kogo_zayavka'].label = "От кого заявка"
        self.fields['description'].label = "Описание"
        self.fields['images'].label = "Изображение"
        # Получите список всех категорий с их деревовидной структурой
        categories_tree = self.get_categories_tree()
        self.fields['cat_post'].widget.choices = categories_tree

    def get_categories_tree(self):
        categories_tree = []

        # Получите все основные категории
        main_categories = Category.objects.filter(parent=None)

        # Переберите основные категории и добавьте их в список с глубиной 0
        for main_category in main_categories:
            # Используйте HTML-код для выделения основной категории жирным шрифтом
            # main_category_name = f'<bold>{main_category.name}</bold>'
            categories_tree.append((main_category.id, main_category.name))
            # Добавьте все подкатегории с глубиной больше 0 рекурсивно
            categories_tree.extend(self.get_subcategories(main_category, 1))
        return categories_tree

    def get_subcategories(self, parent_category, depth):
        subcategories = []
        # Получите все дочерние категории данной родительской категории
        children = parent_category.children.all()
        # Переберите дочерние категории и добавьте их в список с указанной глубиной
        for child in children:
            # Добавьте тире перед именем подкатегории в зависимости от глубины
            child_category_name = "--" * depth + child.name
            subcategories.append((child.id, child_category_name))
            # Если у дочерней категории есть свои дети, добавьте их в список рекурсивно с увеличенной глубиной
            if child.children.exists():
                subcategories.extend(self.get_subcategories(child, depth + 1))
        return subcategories

    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name else obj.username

    class Meta:
        model = Posts
        fields = ['city', 'title', 'description',  'cat_post', 'new_category', 'time_zayavki',
                  'time_glybinie', 'simulyation', 'important', 'images', 'ot_kogo_zayavka', 'second_user']
        widgets = {
            # 'title': forms.TextInput(attrs={'cols': 60}),
            # 'description': forms.Textarea(attrs={'cols': 60, 'rows': 5}),
            'time_zayavki': forms.TimeInput(format='%H:%M'),
            'time_glybinie': forms.TimeInput(format='%H:%M'),
        }

    def clean(self):
        cleaned_data = super().clean()
        cat_post = cleaned_data.get('cat_post')
        new_category = cleaned_data.get('new_category')
        main_category = self.cleaned_data.get('cat_post')
        # print(main_category)

        if main_category.parent is not None and new_category:
            raise forms.ValidationError('Выберите основную категорию!')

        if not cat_post and not new_category:
            raise forms.ValidationError('Выберите категорию или введите новую!')

        if new_category:
            # Проверка уникальности имени категории
            if Category.objects.filter(name=new_category).exists():
                raise forms.ValidationError('Категория с таким именем уже существует!')


class ContactForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label='Сообщение')
    sender = forms.CharField(max_length=100, label='Имя, Фамилия')


