# Generated by Django 2.2.16 on 2022-04-30 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='media/posts/', verbose_name='Картинка'),
        ),
    ]