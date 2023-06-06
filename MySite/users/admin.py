from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_seller', 'rating', 'review', 'email')
    search_fields = ('user', 'email')


admin.site.register(Profile)