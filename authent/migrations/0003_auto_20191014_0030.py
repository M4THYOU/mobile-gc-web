# Generated by Django 2.2.6 on 2019-10-14 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authent', '0002_auto_20191013_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gift_cards',
            field=models.ManyToManyField(blank=True, to='authent.ActiveGiftCard'),
        ),
    ]