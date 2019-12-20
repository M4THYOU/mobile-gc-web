from django.shortcuts import render, HttpResponseRedirect, HttpResponse, Http404
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

import json

from .forms import LoginForm, RegisterForm
from .models import User, CartGiftCard, ActiveGiftCard, Order
from frontend.models import ViewableGiftCard

from Utils.checkout import calculate_total
from Utils.email_funcs import *
from Utils.stripe_funcs import divide_purchase


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

# Create your views here.


class Activate(View):

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return HttpResponseRedirect('/browse/')

        else:
            return HttpResponseRedirect('/account/send-activate/' + str(user.id))  # possible error is user = None


class Login(View):

    def get(self, request):
        is_auth = request.user.is_authenticated

        if is_auth:
            return HttpResponseRedirect('/account/')
        else:
            login_form = LoginForm()
            register_form = RegisterForm()

            data_dict = {
                'is_authenticated': is_auth,
                'login_form': login_form,
                'register_form': register_form
            }
            return render(request, 'login.html', data_dict)

    def post(self, request):
        is_auth = request.user.is_authenticated
        login_form = LoginForm(request.POST)
        register_form = RegisterForm(request.POST)

        if not is_auth:
            if login_form.is_valid():
                user = login_form.get_auth_user()

                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect('/browse/')

            elif register_form.is_valid():
                cd = register_form.cleaned_data

                email = cd['username']
                first_name = cd['first_name']
                last_name = cd['last_name']
                password = cd['password']

                try:
                    new_user = User.objects.get(username=email)
                    if not new_user.is_placeholder:
                        return HttpResponseRedirect('/account/login/')
                    new_user.first_name = first_name
                    new_user.last_name = last_name
                except User.DoesNotExist:
                    new_user = User.objects.create(username=email, first_name=first_name, last_name=last_name, email=email)

                new_user.set_password(password)
                new_user.is_active = False
                new_user.is_placeholder = False
                new_user.save()

                if new_user is not None:
                    return HttpResponseRedirect('/account/send-activate/' + str(new_user.id))

        data_dict = {
            'is_authenticated': is_auth,
            'login_form': login_form,
            'register_form': register_form
        }
        return render(request, 'login.html', data_dict)


class VerifyEmail(View):

    def get(self, request, user_id):
        requested_user = User.objects.get(id=user_id)
        if requested_user.is_active:
            return Http404
        else:
            domain = get_current_site(request).domain
            send_activation_email(requested_user, domain)
            return render(request, 'verification-sent.html', {'user': requested_user})


class Logout(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class Account(View):

    def get(self, request):
        current_user = request.user
        is_auth = current_user.is_authenticated

        if is_auth:
            user_cards = current_user.gift_cards.all()

            data_dict = {
                'is_authenticated': is_auth,
                'current_user': current_user,
                'gift_cards': user_cards
            }
            return render(request, 'profile.html', data_dict)
        else:
            return HttpResponseRedirect('/account/login/')


class AddToCart(View):

    def get(self, request, card_slug):
        user = request.user

        if not user.is_authenticated:
            return HttpResponseRedirect('/account/login/')

        viewable_card = ViewableGiftCard.objects.get(slug=card_slug)
        merchant_name = viewable_card.merchant_name
        card_key = viewable_card.card_key
        stripe_acct_id = viewable_card.stripe_acct_id

        cart_card = CartGiftCard.objects.create(merchant_name=merchant_name, card_key=card_key, user_key=user,
                                                stripe_acct_id=stripe_acct_id)
        user.cart_cards.add(cart_card)

        return HttpResponseRedirect('/my-cart/')


class RemoveFromCart(View):

    def get(self, request, card_id):
        user = request.user

        if not user.is_authenticated:
            return HttpResponseRedirect('/account/login/')

        current_card = CartGiftCard.objects.get(id=card_id)

        if current_card.user_key.username != user.username:
            return Http404
        if user.cart_cards.get(id=card_id) is None:  # if it don't exist, it won't be None. Just throws error instead.
            return Http404

        current_card.delete()

        return HttpResponseRedirect('/my-cart/')


class UpdateBeforeCheckout(View):

    def post(self, request):
        data = {}
        for key in request.POST.dict().keys():
            data = json.loads(key)

        # Assumes the order of the list in the post request is the same as the user's card carts.
        # Minimum of 5 for value. Minimum of 1 for quantity. Quantity must be an integer.

        user = request.user
        if not user.is_authenticated:
            return Http404

        data = data['data']
        cart_cards = user.cart_cards.all()

        if len(data) != len(cart_cards):
            return Http404

        for data_item, cart_card in zip(data, cart_cards):
            try:
                val = float(data_item['value'])
            except ValueError:
                val = 5
            try:
                qty = float(data_item['quantity'])
            except ValueError:
                qty = 1

            cart_card.current_card_value = max(val, 5)  # minimum of 5.
            cart_card.quantity = max(qty, 1)  # minimum of 1.

            email = data_item['receiver_email']
            if is_valid_email(email):
                cart_card.receiver_username = email
            else:
                cart_card.receiver_username = ''

            cart_card.save()

        return HttpResponse('Success')


class RetrievePayment(View):

    # in_cents must be an int, either 0 (for false) or 1 (for true).
    def get(self, request, in_cents):
        user = request.user
        is_auth = user.is_authenticated

        payment_dict = {}
        if is_auth:
            cart_cards = user.cart_cards.all()

            if cart_cards:  # make sure it's not empty.
                total = calculate_total(cart_cards, in_cents=bool(in_cents))
                payment_dict['total'] = total

        return JsonResponse(payment_dict)


class HandlePurchase(View):

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Http404

        cart_cards = user.cart_cards.all()
        account_to_price_ref = {}
        transfer_group = None
        for card in cart_cards:
            receiver = card.receiver_username
            merchant_name = card.merchant_name
            current_card_value = card.current_card_value
            card_key = card.card_key
            stripe_acct_id = card.stripe_acct_id

            sender_user = user

            if transfer_group is None:
                transfer_group = card.transfer_group

            if not receiver:  # not being sent as a gift, the card is for thyself.
                for _ in range(0, card.quantity):
                    receiver_user = user

                    new_card = ActiveGiftCard.objects.create(merchant_name=merchant_name,
                                                             current_card_value=current_card_value, card_key=card_key,
                                                             user_key=receiver_user, sender_key=sender_user,
                                                             stripe_acct_id=stripe_acct_id)

                    user.gift_cards.add(new_card)

                    try:
                        account_to_price_ref[stripe_acct_id] += current_card_value
                    except KeyError:
                        account_to_price_ref[stripe_acct_id] = current_card_value

            else:  # card is being sent as a gift
                for _ in range(0, card.quantity):
                    try:  # if it works, the receiver already has an account on the platform.
                        receiver_user = User.objects.get(username=receiver)
                        new_user = False

                    except User.DoesNotExist:  # otherwise, the email entered doesn't actually have an account (YET).
                        receiver_user = User.objects.create(username=receiver, email=receiver)
                        receiver_user.is_active = False
                        receiver_user.is_placeholder = True

                        receiver_user.save()
                        new_user = True

                    new_card = ActiveGiftCard.objects.create(merchant_name=merchant_name,
                                                             current_card_value=current_card_value, card_key=card_key,
                                                             user_key=receiver_user, sender_key=sender_user,
                                                             stripe_acct_id=stripe_acct_id)

                    receiver_user.gift_cards.add(new_card)

                    domain = get_current_site(request).domain

                    if new_user:
                        send_gift_received(receiver_user, sender_user, new_card, domain)
                    else:
                        send_gift_received_with_account(receiver_user, sender_user, new_card, domain)

                    try:
                        account_to_price_ref[stripe_acct_id] += current_card_value
                    except KeyError:
                        account_to_price_ref[stripe_acct_id] = current_card_value

            user.cart_cards.remove(card)
            card.delete()

        order = Order.objects.get(transfer_group=transfer_group)
        order.is_complete = True
        order.save()

        divide_purchase(account_to_price_ref, transfer_group)

        return HttpResponse('/account/')
