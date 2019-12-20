from django.db.models import *


class Transaction(Model):
    # requires: user_key must be a user with a valid connected_acct_id.
    user_key = ForeignKey('authent.User', on_delete=DO_NOTHING)

    price = IntegerField()

    def __str__(self):
        return str(self.id)
