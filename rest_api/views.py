from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import Http404
from django.http import JsonResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from authent.models import User
from Utils.custom_tokens import payment_token

import decimal
import locale

# Create your models here.


class Test(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'TEST'}
        return Response(content)


class MakePayment(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None:
            transaction = None

            for transaction in user.transactions.all():
                check = payment_token.check_token(user, token, transaction.id)
                if check:
                    transaction = transaction
                    break

            if transaction is not None:
                price = transaction.price  # the price is in cents
                real_price = price / 100  # so divide by 100 to get the dollar amount.

                paying_user = request.user

                if not paying_user.is_authenticated:
                    raise Http404

                for gc in paying_user.gift_cards.all():
                    if gc.stripe_acct_id == user.connected_acct_id:
                        gc_bal = gc.current_card_value

                        if real_price > gc_bal:
                            real_price = decimal.Decimal(real_price) - gc_bal
                            gc.delete()
                        elif real_price == gc_bal:
                            real_price = 0
                            gc.delete()
                            break
                        else:  # real_price < gc_bal
                            new_gc_bal = gc_bal - decimal.Decimal(real_price)
                            real_price = 0

                            gc.current_card_value = new_gc_bal
                            gc.save()
                            break

                print('Remaining amount owed:', real_price)
                if real_price == 0:
                    message = 'Payment Successful.'
                else:
                    message = 'All cards have been used. You still owe: ' + locale.currency(real_price)

                transaction.delete()

                response_dict = {
                    'message': message
                }

                return JsonResponse(response_dict)
