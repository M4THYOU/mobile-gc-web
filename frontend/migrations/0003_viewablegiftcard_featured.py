# Generated by Django 2.2.6 on 2019-10-12 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_auto_20191012_0308'),
    ]

    operations = [
        migrations.AddField(
            model_name='viewablegiftcard',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]
