# Generated by Django 4.2.2 on 2023-06-22 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0012_remove_posts_images_posts_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customimage',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_images', to='Blog.posts'),
        ),
    ]
