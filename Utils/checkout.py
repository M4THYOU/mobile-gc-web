import decimal
import locale
import re


def calculate_subtotal(cart_cards):
    """
    Calculates the subtotal (price, excluding service fee) of all cards in a user's cart.
    :param cart_cards: QuerySet of CartCards from the user at hand's cart_cards field.
    :return: Float. The subtotal.
    """

    subtotal = 0
    for card in cart_cards:
        quantity = card.quantity
        value = card.current_card_value

        card_cost = quantity * value
        subtotal += card_cost

    return subtotal


def calculate_subtotal_and_cards(cart_cards):
    """
    Calculates the subtotal (price, excluding service fee) of all cards in a user's cart AND gives a list containing the
        price, quantity, and merchant_name of each card in the cart.
    :param cart_cards: QuerySet of CartCards from the user at hand's cart_cards field.
    :return: Tuple (Float (Subtotal), List of Dicts)
    """

    cards = []  # each item is a dict with name, quantity,
    subtotal = 0
    for card in cart_cards:
        quantity = card.quantity
        value = card.current_card_value
        name = card.merchant_name

        card_cost = quantity * value
        subtotal += card_cost

        item = {
            'name': name,
            'quantity': quantity,
            'card_cost': locale.currency(card_cost)
        }
        cards.append(item)

    return subtotal, cards


def calculate_service_fee(subtotal):
    """
    Calculates the service fee charged based on the amount of money being processed.
    Price:
        $0.20 per $5.00 processed.
    Simplified:
        $0.04 per $1.00 processed.
    :param subtotal: Float. The amount of money being processed.
    :return: Float. The service fee being charged.
    """
    fee_per_dollar_processed = 0.04
    raw_fee = subtotal * decimal.Decimal(fee_per_dollar_processed)
    currency_fee = raw_fee
    return currency_fee


def currency_val_to_float(currency_val):
    """
    Converts a locale.currency value to a float, which is nicely rounded (done by locale.currency).
    :param currency_val: String. Created by locale.currency().
    :return: Float. The numerical representation of the float.
    """
    currency_float = decimal.Decimal(re.sub(r'[^\d.]', '', currency_val))
    return currency_float


def round_price_to_cents(price, in_cents=False):
    """
    Rounds the given price, in dollars, to the integer representing the number of cents.
    :param price: Float. Price, in dollars.
    :param in_cents: Bool. Whether or not to return the value in cents, as opposed to dollars.
    """
    currency_total = locale.currency(price)
    rounded_total = currency_val_to_float(currency_total)

    if in_cents:
        rounded_total = rounded_total * 100

    return rounded_total


def calculate_total(cart_cards, in_cents=False):
    """
    Calculates the total price a user owes, based on the cards in their cart.
    :param cart_cards: QuerySet of CartCards from the user at hand's cart_cards field.
    :param in_cents: Bool. Whether or not to return the value in cents, as opposed to dollars.
    :return: Float. The total price of the user's cart.
    """
    subtotal = calculate_subtotal(cart_cards)
    service_fee = calculate_service_fee(subtotal)

    total = subtotal + service_fee

    rounded_total = round_price_to_cents(total, in_cents)

    return rounded_total
