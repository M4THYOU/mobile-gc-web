from django.shortcuts import render, HttpResponseRedirect
from django.views import View

import locale

from .models import ViewableGiftCard
from authent.models import Order

from Utils.checkout import calculate_service_fee, calculate_subtotal_and_cards, currency_val_to_float
from Utils.stripe_funcs import create_intent


locale.setlocale(locale.LC_ALL, 'en_CA.UTF-8')


# Create your views here.


class Home(View):

    def get(self, request):
        first_featured = ViewableGiftCard.objects.get(featured1=True)
        second_featured = ViewableGiftCard.objects.get(featured2=True)

        all_cards = ViewableGiftCard.objects.all()

        data_dict = {
            'is_authenticated': request.user.is_authenticated,
            'first_featured': first_featured,
            'second_featured': second_featured,
            'all_cards': all_cards
        }
        return render(request, 'index.html', data_dict)


class SingleCard(View):

    def get(self, request, slug):
        current_card = ViewableGiftCard.objects.get(slug=slug)

        data_dict = {
            'is_authenticated': request.user.is_authenticated,
            'current_card': current_card
        }
        return render(request, 'single-card.html', data_dict)


class Browse(View):

    def get(self, request):
        all_cards = ViewableGiftCard.objects.all()

        data_dict = {
            'is_authenticated': request.user.is_authenticated,
            'all_cards': all_cards
        }
        return render(request, 'browse.html', data_dict)


class Contact(View):

    def get(self, request):
        return render(request, 'contact.html', {'is_authenticated': request.user.is_authenticated})


class Cart(View):

    def get(self, request):
        user = request.user
        is_auth = user.is_authenticated

        if is_auth:
            cart_cards = user.cart_cards.all()

            data_dict = {
                'is_authenticated': is_auth,
                'cart_cards': cart_cards
            }
            return render(request, 'cart.html', data_dict)
        else:
            return HttpResponseRedirect('/account/login/')


class Checkout(View):

    def get(self, request):
        user = request.user
        is_auth = user.is_authenticated

        if is_auth:
            cart_cards = user.cart_cards.all()

            if not cart_cards:
                return HttpResponseRedirect('/browse/')

            subtotal, cards = calculate_subtotal_and_cards(cart_cards)

            service_fee = calculate_service_fee(subtotal)
            total = subtotal + service_fee

            formatted_subtotal = locale.currency(subtotal)
            formatted_service_fee = locale.currency(service_fee)
            formatted_total = locale.currency(total)

            cents_total = int(currency_val_to_float(formatted_total) * 100)

            order = Order.objects.create(user_key=user, cents_total=cents_total)
            user.apply_cart_transfer_group(order)
            payment_intent = create_intent(cents_total, 'cad', order)

            data_dict = {
                'user': user,
                'is_authenticated': is_auth,
                'cards': cards,
                'subtotal': formatted_subtotal,
                'service_fee': formatted_service_fee,
                'total': formatted_total,
                'intent': payment_intent
            }
            return render(request, 'checkout.html', data_dict)
        else:
            return HttpResponseRedirect('/account/login/')


########################################################################################################################


class Confirmation(View):

    def get(self, request):
        return render(request, 'confirmation.html', {'is_authenticated': request.user.is_authenticated})
