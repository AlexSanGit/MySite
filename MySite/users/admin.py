from django.contrib import admin
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_seller', 'rating', 'review', 'city',)
    search_fields = ('city', 'name', 'phone')


admin.site.register(Profile, ProfileAdmin)
