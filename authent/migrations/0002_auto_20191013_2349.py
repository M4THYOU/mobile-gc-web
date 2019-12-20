# Generated by Django 2.2.6 on 2019-10-13 23:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0013_giftcardimage_merchant_name'),
        ('authent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveGiftCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_name', models.CharField(max_length=100, unique=True)),
                ('current_card_value', models.DecimalField(decimal_places=2, max_digits=4)),
                ('card_key', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='frontend.GiftCardImage')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='gift_cards',
            field=models.ManyToManyField(to='authent.ActiveGiftCard'),
        ),
    ]
