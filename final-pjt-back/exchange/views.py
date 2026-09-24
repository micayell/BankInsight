from django.conf import settings
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import date, timedelta
import requests
import logging

logger = logging.getLogger(__name__)

def _fetch_exchange_data_with_fallback(base_date):
    """
    주어진 날짜를 기준으로 환율 데이터를 가져옵니다.
    데이터가 없으면(빈 리스트), 최대 7일 전까지 하루씩 이전 날짜로 재시도합니다.
    API 에러 발생 시에는 즉시 중단합니다.
    """
    EXCHANGE_API_KEY = settings.EXCHANGE_API_KEY
    for i in range(7):
        search_date = base_date - timedelta(days=i)
        
        # 공지사항에 따라 기존 www.koreaexim.go.kr 도메인이 종료되고 oapi.koreaexim.go.kr 로 변경됨
        url = 'https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON'
        params = {
            'authkey': EXCHANGE_API_KEY,
            'searchdate': search_date.strftime("%Y%m%d"),
            'data': 'AP01'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Case 1: 데이터가 없는 날짜 (휴일 등) -> 빈 리스트 [] 반환
            if not data:
                continue

            # Case 2: API가 에러 코드를 반환 (e.g., 잘못된 API 키)
            if isinstance(data, list) and data[0].get('result') != 1:
                error_message = data[0].get('errmsg', 'Unknown API Error')
                # 재시도해도 소용없는 에러이므로 즉시 예외 발생
                raise requests.exceptions.RequestException(f"Exchange API returned an error: {error_message}")

            # Case 3: 성공
            return data, search_date

        except requests.exceptions.HTTPError as e:
            # 404 등 실제 HTTP 에러 발생 시 재시도
            logger.warning(f'HTTPError for {search_date}: {e}. Trying previous day.')
            continue
        except requests.exceptions.RequestException as e:
            # 직접 발생시킨 API 에러 또는 타임아웃 등 다른 요청 에러
            logger.error(f"A request exception occurred: {e}")
            raise # 이 에러는 뷰에서 처리하도록 다시 발생시킴

    # 7일간의 재시도 후에도 데이터를 찾지 못한 경우
    return None, None

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def exchangetoday(request):
    """가장 최신 영업일의 환율 정보를 반환합니다."""
    try:
        result, found_date = _fetch_exchange_data_with_fallback(date.today())
        
        if result:
            return Response(result)
        else:
            return Response({'error': '최근 7일간 환율 데이터를 가져오지 못했습니다.'}, status=status.HTTP_404_NOT_FOUND)

    except requests.exceptions.RequestException as e:
        logger.error(f"Exchange API RequestException: {str(e)}")
        return Response({'error': '외부 환율 API 호출 중 오류가 발생했습니다.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(f"Internal Server Error in exchangetoday: {str(e)}")
        return Response({'error': '서버 내부 오류가 발생했습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def exchangeyesterday(request):
    """가장 최신 영업일의 바로 이전 영업일의 환율 정보를 반환합니다."""
    try:
        _, latest_date = _fetch_exchange_data_with_fallback(date.today())
        if not latest_date:
            return Response({'error': '최신 환율 데이터를 찾을 수 없어 이전 데이터를 조회할 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        yesterday_base = latest_date - timedelta(days=1)
        result, found_date = _fetch_exchange_data_with_fallback(yesterday_base)

        if result:
            return Response(result)
        else:
            return Response({'error': '이전 영업일의 환율 데이터를 가져오지 못했습니다.'}, status=status.HTTP_404_NOT_FOUND)

    except requests.exceptions.RequestException as e:
        logger.error(f"Exchange API RequestException: {str(e)}")
        return Response({'error': '외부 환율 API 호출 중 오류가 발생했습니다.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(f"Internal Server Error in exchangeyesterday: {str(e)}")
        return Response({'error': '서버 내부 오류가 발생했습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
