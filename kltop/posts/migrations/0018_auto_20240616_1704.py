# Generated by Django 2.2.16 on 2024-06-16 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20240616_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(help_text='Введите текст названия статьи', max_length=100, verbose_name='Название статьи'),
        ),
    ]