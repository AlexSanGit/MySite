from django.contrib.auth.models import AbstractUser
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class User(models.Model):
    PASSENGER = 'P'
    DRIVER = 'D'
    USER_TYPE_CHOICES = (
        (PASSENGER, 'Passenger'),
        (DRIVER, 'Driver'),
    )
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.name


class Driver(models.Model):
    FREE = 'F'
    BUSY = 'B'
    DRIVER_STATUS_CHOICES = (
        (FREE, 'Free'),
        (BUSY, 'Busy'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    driver_status = models.CharField(max_length=1, choices=DRIVER_STATUS_CHOICES)

    def __str__(self):
        return self.user.name


class Taxi(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)

    def __str__(self):
        return f'Taxi {self.id}'


# class CustomUser(AbstractUser):
#     is_driver = models.BooleanField(default=False)
#     is_passenger = models.BooleanField(default=False)
#
#
# class Taxi(models.Model):
#     driver = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='taxi')
#     is_available = models.BooleanField(default=True)
