# Generated by Django 2.2.6 on 2019-10-24 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authent', '0013_activegiftcard_stripe_acct_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activegiftcard',
            name='stripe_acct_id',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='cartgiftcard',
            name='stripe_acct_id',
            field=models.CharField(max_length=200),
        ),
    ]
