from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, ActiveGiftCard, CartGiftCard, Order
from .forms import CustomUserChangeForm

# Register your models here.


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('gift_cards', 'cart_cards', 'is_placeholder', 'connected_acct_id', 'transactions')}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(ActiveGiftCard)
admin.site.register(CartGiftCard)
admin.site.register(Order)
