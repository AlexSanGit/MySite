# Generated by Django 4.2.2 on 2023-06-18 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0006_image_posts_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Blog.posts'),
        ),
        migrations.RemoveField(
            model_name='posts',
            name='images',
        ),
        migrations.AddField(
            model_name='posts',
            name='images',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Blog.image'),
        ),
    ]
