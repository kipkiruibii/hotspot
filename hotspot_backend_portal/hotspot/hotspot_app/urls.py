from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("initiate_pay",views.paymentSTK, name='initiate_payment'),
    path("payHeroCallback/", views.payHeroCallback, name="payHeroCallback"),
    path("get_login_link", views.get_login_link, name="get_login_link"),
]
