import stripe

stripe.api_key = 'sk_test_tYFVBPxzwiMxf2k5kgRK9ZZn00XEXFZzld'  # testing
# stripe.api_key = 'sk_live_bYasAo0E7eDV3J2QHoZvQE3q009IvWLsFA'  # production

# Test card: 4000001240000000


def create_intent(amount, currency, order):
    """
    Creates a Stripe PaymentIntent object.
    :param amount: Integer. Value to be charged, in cents.
    :param currency: String, three letters. Represents the currency of the charge.
    :param order: Order. Contains the unique string, transfer_group, which identifies all cards being transferred.
    :return: PaymentIntent to be sent to the frontend and stripe.js.
    """
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        transfer_group=order.transfer_group
    )

    return intent


def charges_data(payment_intent_id):
    """
    Returns the charge data for the recent purchase.
    :param payment_intent_id: String. Generated from stripe.js on the client after a charge.
    :return: Dict with data from the charge.
    """
    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    charges = intent.charges.data

    return charges


def divide_purchase(account_to_price_ref, transfer_group):
    """
    Creates and sends transfers to each connected account being purchases from.
    :param account_to_price_ref: Dict. ['stripe_acct_id': fee_owed]
    :param transfer_group: Unique string which identifies all cards being transferred.
    """

    for acct_id, fee_owed in account_to_price_ref.items():
        fee_owed_cents = int(float(fee_owed) * 100)

        stripe.Transfer.create(
            amount=fee_owed_cents,
            currency='cad',
            destination=acct_id,
            transfer_group=transfer_group
        )
