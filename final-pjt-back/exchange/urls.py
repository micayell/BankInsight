from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('today/', views.exchangetoday),
    path('yesterday/',views.exchangeyesterday)
]
