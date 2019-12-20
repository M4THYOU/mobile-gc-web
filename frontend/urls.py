from django.urls import path

from frontend import views

urlpatterns = [
    # Check Server
    path('', views.Home.as_view(), name='home'),
    path('browse/<slug:slug>/', views.SingleCard.as_view(), name='single-card'),
    path('browse/', views.Browse.as_view(), name='browse'),
    path('contact/', views.Contact.as_view(), name='contact'),
    path('my-cart/', views.Cart.as_view(), name='my-cart'),
    path('checkout/', views.Checkout.as_view(), name='checkout'),

    path('confirmation/', views.Confirmation.as_view(), name='confirmation'),

]
