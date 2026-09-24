import datetime
import uuid
import logging
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)

def generate_kftc_tran_id():
    """KFTC 거래고유번호(고객이 할당받은 기관코드 9자리 + 난수 11자리)를 생성해야 하지만,
    단순 20자리 제한이 있을 수 있으니 UUID 앞 20자리만 사용"""
    return str(uuid.uuid4()).replace('-', '')[:20]

def generate_kftc_tran_dtm():
    """거래일시: YYYYMMDDHHMMSSms (17자리)"""
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def kftc_callback(request):
    code = request.GET.get('code')
    return Response({"message": "인가 고유 코드", "code": code})

def get_bounding_box(lat, lng, offset=0.02):
    """위경도 중심으로 사각형 검색 범위 계산"""
    return str(lat - offset), str(lng - offset), str(lat + offset), str(lng + offset)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_atm_list(request):
    """KFTC 금융MAP - [ATM정보조회] 엔드포인트 연동"""
    try:
        lat = float(request.GET.get('lat', 37.498))
        lng = float(request.GET.get('lng', 127.027))
    except (TypeError, ValueError):
        lat, lng = 37.498, 127.027
        
    tran_id = generate_kftc_tran_id()
    tran_dtm = generate_kftc_tran_dtm()
    start_lat, start_lng, end_lat, end_lng = get_bounding_box(lat, lng)

    url = 'https://openapi.finmap.or.kr/v1.0/kftc/inquiry/atm_lists'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "api_tran_id": tran_id,
        "api_tran_dtm": tran_dtm,
        "start_latitude": start_lat,
        "start_longitude": start_lng,
        "end_latitude": end_lat,
        "end_longitude": end_lng,
        "mob_cash_card_psb_yn": "N"
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        if resp.status_code == 200:
            return Response(resp.json())
        else:
            logger.error(f"KFTC ATM 에러: {resp.status_code} - {resp.text}")
            return Response({
                "error": "KFTC 서버 통신 실패",
                "status_code": resp.status_code,
                "detail": resp.text
            }, status=500)
    except requests.exceptions.RequestException as e:
        logger.error(f"KFTC ATM 통신(네트워크) 실패: {str(e)}")
        return Response({"error": "네트워크/결제원 서버 연결 오류", "detail": str(e)}, status=500)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_branch_list(request):
    """KFTC 금융MAP - [지점정보조회] 엔드포인트 연동"""
    try:
        lat = float(request.GET.get('lat', 37.498))
        lng = float(request.GET.get('lng', 127.027))
    except (TypeError, ValueError):
        lat, lng = 37.498, 127.027
        
    tran_id = generate_kftc_tran_id()
    tran_dtm = generate_kftc_tran_dtm()
    start_lat, start_lng, end_lat, end_lng = get_bounding_box(lat, lng)

    url = 'https://openapi.finmap.or.kr/v1.0/kftc/inquiry/brch_lists'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "api_tran_id": tran_id,
        "api_tran_dtm": tran_dtm,
        "start_latitude": start_lat,
        "start_longitude": start_lng,
        "end_latitude": end_lat,
        "end_longitude": end_lng
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        if resp.status_code == 200:
            return Response(resp.json())
        else:
            logger.error(f"KFTC Branch 에러: {resp.status_code} - {resp.text}")
            return Response({
                "error": "KFTC 서버 통신 실패",
                "status_code": resp.status_code,
                "detail": resp.text
            }, status=500)
    except requests.exceptions.RequestException as e:
        logger.error(f"KFTC Branch 통신(네트워크) 실패: {str(e)}")
        return Response({"error": "네트워크/결제원 서버 연결 오류", "detail": str(e)}, status=500)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_atm_detail(request):
    """KFTC 금융MAP - [ATM정보상세조회] 엔드포인트 연동"""
    trns_org_code = request.GET.get('trns_org_code') or request.POST.get('trns_org_code')
    atm_no = request.GET.get('atm_no') or request.POST.get('atm_no')
    dup_atm_no = request.GET.get('dup_atm_no') or request.POST.get('dup_atm_no', "00")
        
    tran_id = generate_kftc_tran_id()
    tran_dtm = generate_kftc_tran_dtm()

    url = 'https://openapi.finmap.or.kr/v1.0/kftc/inquiry/atm_detail'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "api_tran_id": tran_id,
        "api_tran_dtm": tran_dtm,
        "trns_org_code": trns_org_code or "002",
        "atm_no": atm_no or "0021234CD01",
        "dup_atm_no": dup_atm_no
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        if resp.status_code == 200:
            return Response(resp.json())
        else:
            logger.error(f"KFTC ATM Detail 에러: {resp.status_code} - {resp.text}")
            return Response({
                "error": "KFTC 서버 통신 실패",
                "status_code": resp.status_code,
                "detail": resp.text
            }, status=500)
    except requests.exceptions.RequestException as e:
        logger.error(f"KFTC ATM Detail 통신 실패: {str(e)}")
        return Response({"error": "네트워크/결제원 서버 연결 오류", "detail": str(e)}, status=500)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_branch_detail(request):
    """KFTC 금융MAP - [지점정보상세조회] 엔드포인트 연동"""
    trns_org_code = request.GET.get('trns_org_code') or request.POST.get('trns_org_code')
    brch_code = request.GET.get('brch_code') or request.POST.get('brch_code')
    dup_brch_code = request.GET.get('dup_brch_code') or request.POST.get('dup_brch_code', "00")
        
    tran_id = generate_kftc_tran_id()
    tran_dtm = generate_kftc_tran_dtm()

    url = 'https://openapi.finmap.or.kr/v1.0/kftc/inquiry/brch_detail'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "api_tran_id": tran_id,
        "api_tran_dtm": tran_dtm,
        "trns_org_code": trns_org_code or "002",
        "brch_code": brch_code or "0021234",
        "dup_brch_code": dup_brch_code
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        if resp.status_code == 200:
            return Response(resp.json())
        else:
            logger.error(f"KFTC Branch Detail 에러: {resp.status_code} - {resp.text}")
            return Response({
                "error": "KFTC 서버 통신 실패",
                "status_code": resp.status_code,
                "detail": resp.text
            }, status=500)
    except requests.exceptions.RequestException as e:
        logger.error(f"KFTC Branch Detail 통신 실패: {str(e)}")
        return Response({"error": "네트워크/결제원 서버 연결 오류", "detail": str(e)}, status=500)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_atm_fee(request):
    """KFTC 금융MAP - [수수료정보조회] 엔드포인트 연동"""
    trns_org_code = request.GET.get('trns_org_code') or request.POST.get('trns_org_code')
    org_type_code = request.GET.get('org_type_code') or request.POST.get('org_type_code')
        
    tran_id = generate_kftc_tran_id()
    tran_dtm = generate_kftc_tran_dtm()

    url = 'https://openapi.finmap.or.kr/v1.0/kftc/inquiry/atm_fee'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "api_tran_id": tran_id,
        "api_tran_dtm": tran_dtm,
        "trns_org_code": trns_org_code or "007",
        "org_type_code": org_type_code or "009"
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        if resp.status_code == 200:
            return Response(resp.json())
        else:
            logger.error(f"KFTC ATM Fee 에러: {resp.status_code} - {resp.text}")
            return Response({
                "error": "KFTC 서버 통신 실패",
                "status_code": resp.status_code,
                "detail": resp.text
            }, status=500)
    except requests.exceptions.RequestException as e:
        logger.error(f"KFTC ATM Fee 통신 실패: {str(e)}")
        return Response({"error": "네트워크/결제원 서버 연결 오류", "detail": str(e)}, status=500)
