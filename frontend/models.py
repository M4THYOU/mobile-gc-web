from django.db.models import *
from django.template.defaultfilters import slugify

# Create your models here.


class ViewableGiftCard(Model):
    merchant_name = CharField(max_length=100, unique=True)
    description = CharField(max_length=700)  # CharField is used here vs a TextField because the latter's max_length is
    # not enforced at the database level, unlike the former.
    one_liner = CharField(max_length=150)  # Just a one line description of the merchant. "Authentic Italian Cuisine".

    max_value = IntegerField()
    featured1 = BooleanField(default=False)  # This can only be true for 1 card!
    featured2 = BooleanField(default=False)  # This can only be true for 1 card!
    card_key = ForeignKey('GiftCardImage', on_delete=DO_NOTHING)

    slug = SlugField(max_length=100, unique=True)

    stripe_acct_id = CharField(max_length=200, unique=True)

    def __str__(self):
        return self.merchant_name

    def save(self, **kwargs):
        self.slug = slugify(self.merchant_name)

        super(ViewableGiftCard, self).save()


class GiftCardImage(Model):
    merchant_name = CharField(max_length=100, unique=True)
    card_image = ImageField(upload_to='card-images/')

    def __str__(self):
        return self.merchant_name
