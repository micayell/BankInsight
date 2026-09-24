from django.urls import path
from . import views

urlpatterns = [
    path('callback/', views.kftc_callback, name='kftc_callback'),
    path('atm/list/', views.get_atm_list, name='atm_list'),
    path('atm/detail/', views.get_atm_detail, name='atm_detail'),
    path('atm/fee/', views.get_atm_fee, name='atm_fee'),
    path('branch/list/', views.get_branch_list, name='branch_list'),
    path('branch/detail/', views.get_branch_detail, name='branch_detail'),
]
