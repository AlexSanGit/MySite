from Blog.models import *
from django.contrib import admin


class PostAdmin(admin.ModelAdmin):     # Настройка столбов в админке
    list_display = ('id', 'cat_post', 'author', 'title', 'description', 'slug', 'photo_part', 'is_published')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')
    list_editable = ('is_published', )
    list_filter = ('is_published', 'time_create')
    prepopulated_fields = {"slug": ("title",)}


class CategoryAdmin(admin.ModelAdmin):     # Настройка столбов в админке
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')
    search_fields = ('name', )
    prepopulated_fields = {"slug": ("name",)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'article', 'created', 'status', 'text')
    list_filter = ('status', 'created', 'updated')
    search_fields = ('author', 'email', 'text')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_seller', 'rating', 'review', 'email')
    search_fields = ('user', 'email')


admin.site.register(Posts, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comments, CommentAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
