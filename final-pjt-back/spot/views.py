from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from .models import ProductPrice, SilverPrice
from .services import fetch_gold_data, fetch_silver_data
from .serializers import (
    SilverPriceSerializer, 
    GoldPriceHistorySerializer, SilverPriceHistorySerializer
)
from datetime import date, timedelta
import requests

def _fetch_gold_data_with_fallback(api_key: str, target_date: date, max_retries: int = 7):
    """
    지정된 날짜의 금 시세 데이터 조회를 시도하고, 실패(데이터 없음) 시
    하루씩 이전 날짜로 최대 `max_retries` 일까지 재시도합니다.
    """
    for i in range(max_retries):
        current_date = target_date - timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        
        try:
            # 이제 금 데이터만 처리
            fetch_gold_data(api_key, date_str, date_str)
            return
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404: # 데이터가 없는 경우
                print(f"Failed to fetch gold data for {current_date} (Not Found). Retrying with previous day.")
                continue
            raise # 그 외 HTTP 에러는 즉시 실패 처리
        except Exception as e:
            print(f"An unexpected error occurred while fetching gold data for {current_date}: {e}")
            raise

    raise Exception(f"Failed to fetch gold data after {max_retries} retries.")

#금조회
@api_view(['GET'])
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
            _fetch_gold_data_with_fallback(service_key, end_dt)
        else: # 은(silver)인 경우
            fetch_silver_data(start_dt.isoformat(), end_dt.isoformat())
    except Exception as e:
        # 데이터 갱신에 실패하더라도 503 에러를 반환하지 않고, 서버에 로그만 남깁니다.
        # DB에 저장된 기존 데이터를 기반으로 정상 응답을 진행합니다.
        print(f"Could not update {metal} price data, serving from cache. Error: {e}")

    if metal == '금':
        qs = ProductPrice.objects.filter(prod_code=ProductPrice.GOLD_CODE)
        qs = qs.filter(date__gte=start_dt, date__lte=end_dt).order_by('date')
        serializer = GoldPriceHistorySerializer(qs, many=True)
    else:
        qs = SilverPrice.objects.all()
        qs = qs.filter(date__gte=start_dt, date__lte=end_dt).order_by('date')
        serializer = SilverPriceHistorySerializer(qs, many=True)

    return Response(serializer.data)

#은조회
class SilverPriceListAPIView(generics.ListAPIView):
    queryset = SilverPrice.objects.all().order_by('date')
    serializer_class = SilverPriceSerializer
