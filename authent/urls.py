from django.urls import path

from authent import views

urlpatterns = [

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('', views.Account.as_view(), name='my-account'),

    # Ajax
    path('add-to-cart/<slug:card_slug>/', views.AddToCart.as_view(), name='add-to-cart'),
    path('remove-from-cart/<int:card_id>/', views.RemoveFromCart.as_view(), name='remove-from-cart'),
    path('ajax/update-cart/', views.UpdateBeforeCheckout.as_view(), name='update-cart'),
    path('ajax/get-cart-payment/<int:in_cents>/', views.RetrievePayment.as_view(), name='get-cart-payment'),
    path('ajax/make-payment/', views.HandlePurchase.as_view(), name='make-payment'),

    path('send-activate/<int:user_id>/', views.VerifyEmail.as_view(), name='send-activate'),
    path('activate/<str:uidb64>/<str:token>/', views.Activate.as_view(), name='activate'),

]
