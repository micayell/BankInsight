from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('profile/<str:username>/', views.user_profile,   name='user_profile'),
    path('get/interest/',          views.get_interest,    name='get_interest'),
    path('user/delete/<str:username>/', views.user_delete, name='user_delete'),
]