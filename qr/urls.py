from django.urls import path

from qr import views

urlpatterns = [

    path('', views.QRGenerator.as_view(), name='qr-gen'),

    # Token.
    # /token/uid/token/
    # The uid here is the vendor's uid. Not the one making the payment. We get that from request.user.
    # path('token/<str:uidb64>/<str:token>/', views.MakePayment.as_view(), name='make-payment'),



]
