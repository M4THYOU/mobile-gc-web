from django.shortcuts import render, HttpResponseRedirect, HttpResponse, Http404
from django.http import JsonResponse
from django.views import View
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from .forms import QRPriceForm
from .models import Transaction
from Utils.custom_tokens import payment_token
from Utils.checkout import round_price_to_cents
from authent.models import User

import locale
import decimal

# Create your views here.


class QRGenerator(View):

    def get(self, request):
        user = request.user
        is_auth = user.is_authenticated

        if is_auth and user.connected_acct_id:  # if user is authenticated and has an associated connected account.
            price_form = QRPriceForm()

            data_dict = {
                'is_authenticated': is_auth,
                'price_form': price_form
            }
            return render(request, 'qr/landing-page.html', data_dict)

        else:
            return HttpResponseRedirect('/')

    def post(self, request):
        user = request.user
        is_auth = user.is_authenticated
        price_form = QRPriceForm(request.POST)

        if price_form.is_valid() and is_auth and user.connected_acct_id:
            cd = price_form.cleaned_data

            price = cd['price']

            cent_price = int(round_price_to_cents(price, in_cents=True))

            transaction = Transaction.objects.create(user_key=user, price=cent_price)
            user.transactions.add(transaction)

            token = payment_token.make_token(user, transaction.id)
            # host = request.META['HTTP_HOST']  # this returns '127.0.0.1:8000'
            # instead use 192.168.2.12:8000 instead. Just for testing.
            host = '192.168.2.13:8000'
            user_key = urlsafe_base64_encode(force_bytes(user.pk))
            code_url = 'http://{0}/api/token/{1}/{2}/'.format(host, user_key, token)

            data_dict = {
                'code_url': code_url,
                'price': locale.currency(price)
            }
            return render(request, 'qr/show-code.html', data_dict)

        data_dict = {
            'is_authenticated': is_auth,
            'price_form': price_form
        }
        return render(request, 'qr/landing-page.html', data_dict)

"""
class MakePayment(View):

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
"""
