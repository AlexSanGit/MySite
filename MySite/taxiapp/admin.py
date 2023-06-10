from django.contrib import admin
from taxiapp.models import *


class AdminTaxiCity(admin.ModelAdmin):     # Настройка столбов в админке
    list_display = ('name', )


class AdminTaxiUser(admin.ModelAdmin):     # Настройка столбов в админке
    list_display = ('name', 'user_type', 'city', )


class AdminTaxiDriver(admin.ModelAdmin):     # Настройка столбов в админке
    list_display = ('user', 'balance', 'driver_status', )


class AdminTaxiSelectTaxi(admin.ModelAdmin):     # Настройка столбов в админке
    list_display = ('driver',)


admin.site.register(City, AdminTaxiCity)
admin.site.register(User, AdminTaxiUser)
admin.site.register(Driver, AdminTaxiDriver)
admin.site.register(Taxi, AdminTaxiSelectTaxi)
