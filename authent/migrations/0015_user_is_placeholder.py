# Generated by Django 2.2.6 on 2019-11-03 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authent', '0014_auto_20191024_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_placeholder',
            field=models.BooleanField(default=False),
        ),
    ]
