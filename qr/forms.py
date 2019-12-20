from django import forms


class QRPriceForm(forms.Form):
    price = forms.DecimalField(max_digits=6, decimal_places=2)
