from PIL import Image
from django.contrib.auth.models import User
from django.db import models
from users.choices.city_choices import CITY_CHOICES


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_seller = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
    review = models.TextField(blank=True)
    image = models.ImageField(verbose_name='Аватарка', default='default.jpg', upload_to='profile_pics')
    city = models.CharField(verbose_name='Участок', max_length=3, choices=CITY_CHOICES, blank=True)
    phone = models.IntegerField(default=0, blank=True)
    notifications = models.TextField(blank=True, null=True)
    time_glybinie = models.TimeField(blank=True, null=True)
    city_filter = models.CharField(
        max_length=255,  # Укажите подходящую максимальную длину
        blank=True,
    )

    # def __str__(self):
    #     return f'{self.user.username} Profile'
    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (100, 100)
            img.thumbnail(output_size)
            img.save(self.image.path)
