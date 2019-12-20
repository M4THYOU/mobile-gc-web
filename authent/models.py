from django.db.models import *
from django.contrib.auth.models import AbstractUser

import uuid

# Create your models here.


class User(AbstractUser):
    gift_cards = ManyToManyField('ActiveGiftCard', blank=True)
    cart_cards = ManyToManyField('CartGiftCard', blank=True)

    is_placeholder = BooleanField(default=False)

    # If set, this field indicates the user has access to the QR Code Gen page.
    connected_acct_id = CharField(max_length=200, blank=True)
    # If the account is a vendor account, this field contains all the current transaction ids.
    transactions = ManyToManyField('qr.Transaction', blank=True)

    class Meta:
        db_table = 'auth_user'

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password']

    def __str__(self):
        return self.email

    def apply_cart_transfer_group(self, order):
        """
        Sets the transfer_group field of every CartGiftCard in the user's cart_cards.
        :param order: Order.
        """
        for card in self.cart_cards.all():
            card.update_transfer_group(order.transfer_group)
            card.save()


class ActiveGiftCard(Model):
    merchant_name = CharField(max_length=100)
    current_card_value = DecimalField(max_digits=4, decimal_places=2)

    card_key = ForeignKey('frontend.GiftCardImage', on_delete=DO_NOTHING)
    user_key = ForeignKey('authent.User', on_delete=DO_NOTHING)
    sender_key = ForeignKey('authent.User', related_name='sender_key', on_delete=DO_NOTHING)

    stripe_acct_id = CharField(max_length=200)

    def __str__(self):
        return self.merchant_name + str(self.id)


class CartGiftCard(Model):
    merchant_name = CharField(max_length=100)

    card_key = ForeignKey('frontend.GiftCardImage', on_delete=DO_NOTHING)
    user_key = ForeignKey('authent.User', on_delete=DO_NOTHING)

    current_card_value = DecimalField(max_digits=4, decimal_places=2, default=25.00)
    quantity = IntegerField(default=1)
    receiver_username = EmailField(max_length=150, blank=True)  # if still blank, send to myself.

    # comes from Order.transfer_group. Set after payment intent is created.
    transfer_group = CharField(max_length=500, blank=True)
    stripe_acct_id = CharField(max_length=200)

    def __str__(self):
        return self.merchant_name + str(self.id) + ' | Cart'

    def update_transfer_group(self, new_transfer_group):
        """
        Updates the cart_card's transfer group. Tries deleting the old instance of the Order corresponding to
            self.transfer_group, if it exists.
        :param new_transfer_group: String.
        """
        try:
            old_order = Order.objects.get(transfer_group=self.transfer_group)
            old_order.delete()
        except Order.DoesNotExist:
            print('Order already deleted.')
        self.transfer_group = new_transfer_group


class Order(Model):
    user_key = ForeignKey('authent.User', on_delete=DO_NOTHING)
    cents_total = IntegerField()  # this isn't used for anything. We collect it for possible metrics later on.
    transfer_group = CharField(max_length=500, default='UNSET')  # 'order_' + (self.id + 1000)
    is_complete = BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        if self.transfer_group == 'UNSET':
            self.transfer_group = 'order_' + str(self.id + 1000)
            self.save()

    def __str__(self):
        return self.transfer_group
