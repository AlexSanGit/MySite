from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Posts(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100,verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(max_length=255)
    photo_part = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Фото")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(default=True, verbose_name="Публикация")
    cat_post = models.ForeignKey('Category', on_delete=models.PROTECT, blank=True,verbose_name="Категории")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-time_create', ]

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})


class Category(models.Model):
    objects = models.Manager()
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     is_seller = models.BooleanField(default=False)
#     rating = models.IntegerField(default=0)
#     review = models.TextField(blank=True)
#     email = models.EmailField()
#     # avatar = models.ImageField(upload_to="photos/avatar/%Y/%m/%d/", verbose_name="Фото", null=True, blank=True)
#
#     def __str__(self):
#         return str(self.user)


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
