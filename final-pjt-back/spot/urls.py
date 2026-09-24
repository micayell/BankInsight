from django.urls import path
from . import views
from .views import OilPriceListAPIView

urlpatterns = [
    path('', views.spot_price_list),
    path('api/oil-prices/', OilPriceListAPIView.as_view())
]
