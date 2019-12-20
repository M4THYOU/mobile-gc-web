from django.urls import path

from rest_api import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [

    path('test/', views.Test.as_view(), name='test'),
    path('obtain-token/', obtain_auth_token, name='obtain-token'),

    # not to be confused with authtoken from DRF. This is the custom token for making payments.
    path('token/<str:uidb64>/<str:token>/', views.MakePayment.as_view(), name='send-payment')

]
