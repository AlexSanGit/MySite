from io import BytesIO

from PIL.Image import Image
from django.contrib.sites import requests
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from users.models import Profile


class CustomImage(models.Model):
    post = models.ForeignKey('Posts', on_delete=models.CASCADE, null=True, related_name='post_images')
    image = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Изображение")
    objects = models.Manager()

    # def is_valid_image(self):
    #     try:
    #         # Открываем изображение по ссылке и проверяем его целостность
    #         response = requests.get(self.image.url)
    #         img = Image.open(BytesIO(response.content))
    #         img.verify()
    #         return True
    #     except Exception:
    #         return False


class Posts(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(max_length=255)
    photo_part = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Фото")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(default=True, verbose_name="Публикация")
    cat_post = models.ForeignKey('Category', on_delete=models.PROTECT, blank=True, verbose_name="Категории")
    city = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="город", null=True)
    # images = models.ManyToManyField(CustomImage, related_name='posts', blank=True)
    # images = models.ManyToManyField(CustomImage, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-time_create', ]

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})


class Category(MPTTModel):
    objects = models.Manager()
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="Slug")
    # parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    level = models.PositiveIntegerField(default=0)  # Define the default value for the 'level' field
    lft = models.PositiveIntegerField(default=0)  # Определите значение по умолчанию для поля 'lft'
    rght = models.PositiveIntegerField(default=0)  # Определите значение по умолчанию для поля 'rght'

    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']

    def get_all_children(self):
        children = []
        for child in self.get_children():
            children.append(child)
            children.extend(child.get_all_children())
        return children

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']


class Message(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    message = models.TextField()
    sent_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class Offer(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.price


class Comments(models.Model):
    article = models.ForeignKey(Posts, on_delete=models.CASCADE, verbose_name='Статья', blank=True, null=True,
                                related_name='comments_posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор комментария', blank=True, null=True)
    # email = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор комментария', blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)
    text = models.TextField(verbose_name='Текст комментария')
    status = models.BooleanField(verbose_name='Видимость статьи', default=True)

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.author, self.article)
