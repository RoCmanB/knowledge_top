# Generated by Django 2.2.16 on 2024-06-19 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0018_auto_20240616_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.CharField(help_text='Не более 50000 символов', max_length=50000, verbose_name='Введите текст статьи'),
        ),
    ]
