from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import View
from . import views

urlpatterns = [
    path('profile/<str:username>/', views.user_profile,   name='user_profile'),
    path('get/interest/',          views.get_interest,    name='get_interest'),
    path('user/delete/<str:username>/', views.user_delete, name='user_delete'),
    path('email-verify/send/', views.send_email_code, name='send_email_code'),
    path('email-verify/confirm/', views.verify_email_code, name='verify_email_code'),
    path('favorite-bank/', views.toggle_favorite_bank, name='toggle_favorite_bank'),
    
    # dj-rest-auth 비밀번호 재설정 이메일 발송 시 내부 reverse() 에러를 방지하기 위한 더미 URL
    path('password-reset/<uidb64>/<token>/', View.as_view(), name='password_reset_confirm'),
]
