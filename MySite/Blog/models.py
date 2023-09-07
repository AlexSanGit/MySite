from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from users.models import Profile


class CustomImage(models.Model):
    post = models.ForeignKey('Posts', on_delete=models.CASCADE, null=True, related_name='post_images')
    image = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Изображение")
    objects = models.Manager()


class Posts(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(max_length=255)
    photo_part = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Фото")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(default=True, verbose_name="Публикация")
    cat_post = models.ForeignKey('Category', on_delete=models.PROTECT, blank=True, verbose_name="Оборудование")
    city = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Участок", null=True)
    time_zayavki = models.TimeField(verbose_name="Время заявки", default='00:00')
    time_glybinie = models.TimeField(verbose_name="Глубиные:", default='00:00')
    simulyation = models.BooleanField(default=False, verbose_name="Симуляция")


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


# @receiver(post_save, sender=Comments)
# def send_notification_to_author(sender, instance, created, **kwargs):
#     if created:
#         # Получаем автора комментария
#         comment_author = instance.author
#
#         # Получаем автора поста
#         post_author = instance.article.author
#
#         # Формируем URL для просмотра комментария
#         comment_url = reverse('comment_detail',
#                               args=[instance.id])  # Здесь 'comment_detail' - это имя URL для просмотра комментария
#
#         # Формируем текст и html для письма
#         subject = 'У вас новый комментарий к посту'
#         message = f'Здравствуйте, {post_author.username}!\n\nУ вас новый комментарий к вашему посту "{instance.article.title}".\n\nВы можете просмотреть его по этой ссылке:\n{comment_url}'
#         html_message = f'Здравствуйте, {post_author.username}!<br><br>У вас новый комментарий к вашему посту "{instance.article.title}".<br><br>Вы можете просмотреть его по этой <a href="{comment_url}">ссылке</a>.'
#
#         # Отправляем уведомление
#         send_mail(subject, message, None, [post_author.email], html_message=html_message)


# myapp/models.py

@receiver(post_save, sender=Comments)
def send_notification_to_author(sender, instance, created, **kwargs):
    if created:
        # Получаем автора комментария
        comment_author = instance.author

        # Получаем автора поста
        post_author = instance.article.author

        # Закомментируйте или удалите это условие,
        # чтобы уведомления отправлялись даже автору поста
        # if comment_author != post_author:

        # Сохраняем уведомление в профиле пользователя
        profile, created = Profile.objects.get_or_create(user=post_author)
        post_title = instance.article.title
        post_slug = instance.article.slug
        post_link = Posts.objects.get(title=post_title).get_absolute_url()  # Используйте get_absolute_url()
        # post_link = instance.article.get_absolute_url()  # Получаем ссылку на пост
        print(post_link)

        if profile.notifications:
            profile.notifications += f'\nПост "{post_title}" получил новый комментарий. Ссылка: {post_link}'
        else:
            profile.notifications = f'Пост "{post_title}" получил новый комментарий. Ссылка: {post_link}'
        profile.save()
