# Generated by Django 2.2.6 on 2019-10-12 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0005_auto_20191012_2019'),
    ]

    operations = [
        migrations.AddField(
            model_name='viewablegiftcard',
            name='slug',
            field=models.SlugField(default='test', max_length=100),
            preserve_default=False,
        ),
    ]