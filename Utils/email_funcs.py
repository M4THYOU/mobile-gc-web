from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils.html import strip_tags

from .custom_tokens import account_activation_token


# Email

from_email = 'matthew@qwaked.com'


def send_activation_email(user, domain):
    """
    Sends an activation email to the user's entered email.
    :param user: User object. The user who is registering for the first time.
    :param domain: String. The domain used to build a url in the template. Comes from get_current_site(request).domain.
    """
    subject = 'Activate your Qwaked Account!'

    message = render_to_string('email/activate.html', {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user)
    })

    email_addr = user.email

    email = EmailMessage(subject=subject, body=message, from_email=from_email, to=[email_addr])
    email.send()


def send_gift_received_with_account(receiver, sender, card, domain):
    """
    Sends an email to a user with an existing account on Qwaked alerting them they've been gifted a gift card from
    another member.
    :param receiver: User object. The user who receiving the card.
    :param sender: User object. The user who sending the card.
    :param card: ActiveGiftCard. The card being gifted.
    :param domain: String. The domain used to build a url in the template. Comes from get_current_site(request).domain.
    """
    subject = 'You\'ve received a gift card from {0} {1}!'.format(sender.first_name, sender.last_name)

    url_base = 'http://' + domain  # no trailing slash.
    my_cards_url = url_base + '/account/'
    data_dict = {
        'receiver': receiver,
        'sender': sender,
        'card': card,
        'url_base': url_base,
        'my_cards_url': my_cards_url,
    }

    message_html = render_to_string('email/send-gift-with-account.html', data_dict)
    message_raw = strip_tags(message_html)

    email_addr = receiver.email

    email = EmailMultiAlternatives(subject=subject, body=message_raw, from_email=from_email, to=[email_addr])
    email.attach_alternative(message_html, 'text/html')
    email.send()


def send_gift_received(receiver, sender, card, domain):
    """
    Sends an email to a user WITHOUT an existing account on Qwaked alerting them they've been gifted a gift card from
    another member, AND requesting that they sign up to claim the card.
    :param receiver: User object. The user who receiving the card.
    :param sender: User object. The user who sending the card.
    :param card: ActiveGiftCard. The card being gifted.
    :param domain: String. The domain used to build a url in the template. Comes from get_current_site(request).domain.
    """
    subject = 'You\'ve received a gift card from {0} {1}!'.format(sender.first_name, sender.last_name)

    url_base = 'http://' + domain  # no trailing slash.
    my_cards_url = url_base + '/account/'
    data_dict = {
        'receiver': receiver,
        'sender': sender,
        'card': card,
        'url_base': url_base,
        'my_cards_url': my_cards_url,
    }

    message_html = render_to_string('email/send-gift-no-account.html', data_dict)
    message_raw = strip_tags(message_html)

    email_addr = receiver.email

    email = EmailMultiAlternatives(subject=subject, body=message_raw, from_email=from_email, to=[email_addr])
    email.attach_alternative(message_html, 'text/html')
    email.send()


