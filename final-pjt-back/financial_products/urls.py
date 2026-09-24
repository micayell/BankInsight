# final-pjt/back/financial_products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 데이터 로드
    path('load/deposits/', views.load_deposit_products, name='load-deposits'),
    path('load/savings/', views.load_saving_products, name='load-savings'),

    # Deposit 리소스
    path('deposits/', views.deposit_product_list, name='deposit-list'),
    path('deposits/<str:fin_prdt_cd>/', views.deposit_detail, name='deposit-detail'),
    path('deposits/<str:fin_prdt_cd>/options/', views.deposit_option_list, name='deposit-options'),
    path('deposits/<str:fin_prdt_cd>/options/<int:option_id>/',
         views.deposit_option_detail, name='deposit-option-detail'),
    path('deposits/<str:fin_prdt_cd>/like/', views.like_deposit, name='deposit-like'),

    # Saving 리소스
    path('savings/', views.saving_product_list, name='saving-list'),
    path('savings/<str:fin_prdt_cd>/', views.saving_detail, name='saving-detail'),
    path('savings/<str:fin_prdt_cd>/options/', views.saving_option_list, name='saving-options'),
    path('savings/<str:fin_prdt_cd>/options/<int:option_id>/',
         views.saving_option_detail, name='saving-option-detail'),
    path('savings/<str:fin_prdt_cd>/like/', views.like_saving, name='saving-like'),

    # 은행별 조회
    path('banks/<str:bank_name>/deposits/', views.bank_deposit, name='bank-deposits'),
    path('banks/<str:bank_name>/savings/', views.bank_saving, name='bank-savings'),

    # path('users/<str:username>/recommend/deposits/',        views.deposit_recommend,         name='recommend-deposits'),
    # path('users/<str:username>/recommend/deposits/second/', views.deposit_recommend_second,  name='recommend-deposits-age'),
    # path('users/<str:username>/recommend/savings/',         views.saving_recommend,          name='recommend-savings'),
    # path('users/<str:username>/recommend/savings/second/',  views.saving_recommend_second,   name='recommend-savings-age'),

    path('load/mortgages/', views.load_mortgage_loan_products, name='load-mortgages'),
    path('load/jeonses/', views.load_jeonse_loan_products, name='load-jeonses'),
    path('mortgages/', views.mortgage_loan_list, name='mortgage-list'),
    path('mortgages/<str:fin_prdt_cd>/', views.mortgage_loan_detail, name='mortgage-detail'),
    path('mortgages/<str:fin_prdt_cd>/like/', views.like_mortgage_loan, name='mortgage-like'),
    path('jeonses/', views.jeonse_loan_list, name='jeonse-list'),
    path('jeonses/<str:fin_prdt_cd>/', views.jeonse_loan_detail, name='jeonse-detail'),
    path('jeonses/<str:fin_prdt_cd>/like/', views.like_jeonse_loan, name='jeonse-like'),
]

