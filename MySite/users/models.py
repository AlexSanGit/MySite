from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # is_seller = models.BooleanField(default=False)
    # rating = models.IntegerField(default=0)
    # review = models.TextField(blank=True)
    # email = models.EmailField()
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')