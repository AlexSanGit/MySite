# Generated by Django 4.2.2 on 2023-06-11 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile_city_profile_phone'),
        ('Blog', '0004_alter_posts_description_alter_posts_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.profile', verbose_name='город'),
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
