# Generated by Django 2.2.6 on 2019-10-15 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authent', '0009_auto_20191015_0026'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartgiftcard',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
