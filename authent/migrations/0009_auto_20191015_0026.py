# Generated by Django 2.2.6 on 2019-10-15 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authent', '0008_auto_20191014_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartgiftcard',
            name='current_card_value',
            field=models.DecimalField(decimal_places=2, default=25.0, max_digits=4),
        ),
    ]
