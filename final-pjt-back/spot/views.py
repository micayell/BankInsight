from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, generics
from .models import ProductPrice, OilPrice
from .services import fetch_gold_data, fetch_oil_data
from .serializers import (
    OilPriceSerializer, 
    GoldPriceHistorySerializer, OilPriceHistorySerializer
)
from datetime import date, timedelta
import requests

def _fetch_gold_data_with_fallback(api_key: str, target_date: date, max_retries: int = 7):
    for i in range(max_retries):
        current_date = target_date - timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        
        try:
            fetch_gold_data(api_key, date_str, date_str)
            return
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                continue
            raise
        except Exception as e:
            raise

    raise Exception(f"Failed to fetch gold data after {max_retries} retries.")

def _fetch_oil_data_with_fallback(api_key: str, target_date: date, max_retries: int = 7):
    for i in range(max_retries):
        current_date = target_date - timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        
        try:
            fetch_oil_data(api_key, date_str, date_str)
            return
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                continue
            raise
        except Exception as e:
            raise

    raise Exception(f"Failed to fetch oil data after {max_retries} retries.")

@api_view(['GET'])
@permission_classes([AllowAny])
def spot_price_list(request):
    service_key = settings.DATA_GO_API_KEY
    if not service_key:
        return Response(
            {"detail": "DATA_GO_API_KEY not configured"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    metal = request.GET.get('metal', '금')
    start_dt_str = request.GET.get('start')
    end_dt_str = request.GET.get('end')
    
    start_dt = date.fromisoformat(start_dt_str) if start_dt_str else date.today() - timedelta(days=30)
    end_dt = date.fromisoformat(end_dt_str) if end_dt_str else date.today()
    
    if end_dt > date.today():
        end_dt = date.today()

    try:
        if metal == '금':
            qs = ProductPrice.objects.filter(prod_code=ProductPrice.GOLD_CODE, date__gte=start_dt, date__lte=end_dt)
            # 평일만 있으므로 전체 일수의 절반 이하로 데이터가 있다면 과거 데이터가 비어있다고 간주
            if qs.count() < (end_dt - start_dt).days // 2:
                fetch_gold_data(service_key, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'))
            else:
                _fetch_gold_data_with_fallback(service_key, end_dt)
        else: # 석유인 경우
            qs = OilPrice.objects.filter(date__gte=start_dt, date__lte=end_dt)
            if qs.count() < (end_dt - start_dt).days // 2:
                fetch_oil_data(service_key, start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d'))
            else:
                _fetch_oil_data_with_fallback(service_key, end_dt)
    except Exception as e:
        print(f"Could not update {metal} price data, serving from cache. Error: {e}")

    if metal == '금':
        qs = ProductPrice.objects.filter(prod_code=ProductPrice.GOLD_CODE)
        qs = qs.filter(date__gte=start_dt, date__lte=end_dt).order_by('date')
        serializer = GoldPriceHistorySerializer(qs, many=True)
    else:
        qs = OilPrice.objects.all()
        qs = qs.filter(date__gte=start_dt, date__lte=end_dt).order_by('date')
        serializer = OilPriceHistorySerializer(qs, many=True)

    return Response(serializer.data)

class OilPriceListAPIView(generics.ListAPIView):
    queryset = OilPrice.objects.all().order_by('date')
    serializer_class = OilPriceSerializer