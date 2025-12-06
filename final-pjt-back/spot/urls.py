from django.urls import path
from . import views
from .views import SilverPriceListAPIView

urlpatterns = [
    path('', views.spot_price_list),
    path('api/silver-prices/', SilverPriceListAPIView.as_view())
]
