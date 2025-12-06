import requests
from django.conf import settings
from django.db import transaction
from decimal import Decimal, InvalidOperation

from .models import DepositProduct, DepositOption, SavingProduct, SavingOption

API_KEY = settings.FIN_API_KEY
BASE_URL = 'http://finlife.fss.or.kr/finlifeapi'

def _fetch_financial_products(url, params):
    """지정된 URL과 파라미터로 금융 상품 데이터를 요청하고 JSON으로 반환합니다."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 200번대 상태 코드가 아닐 경우 예외 발생
        return response.json()
    except requests.exceptions.RequestException as e:
        # 네트워크 오류 또는 HTTP 오류 처리
        print(f"API 호출 중 오류 발생: {e}")
        return None

def _to_decimal(value):
    """숫자형 문자열을 Decimal로 변환합니다. 변환 실패 시 None을 반환합니다."""
    if value is None:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError):
        return None

@transaction.atomic
def save_deposit_products():
    """정기예금 상품 목록을 API로부터 받아와 데이터베이스에 저장합니다."""
    url = f'{BASE_URL}/depositProductsSearch.json'
    params = {'auth': API_KEY, 'topFinGrpNo': '020000', 'pageNo': 1}
    data = _fetch_financial_products(url, params)

    if not data or 'result' not in data:
        return False

    base_list = data['result'].get('baseList', [])
    option_list = data['result'].get('optionList', [])

    for base in base_list:
        product, created = DepositProduct.objects.update_or_create(
            fin_prdt_cd=base.get('fin_prdt_cd'),
            defaults={
                'dcls_month': base.get('dcls_month'),
                'fin_co_no': base.get('fin_co_no'),
                'kor_co_nm': base.get('kor_co_nm'),
                'fin_prdt_nm': base.get('fin_prdt_nm'),
                'join_way': base.get('join_way'),
                'mtrt_int': base.get('mtrt_int'),
                'spcl_cnd': base.get('spcl_cnd'),
                'join_deny': base.get('join_deny'),
                'join_member': base.get('join_member'),
                'etc_note': base.get('etc_note'),
                'max_limit': _to_decimal(base.get('max_limit')),
            }
        )

    for option in option_list:
        product = DepositProduct.objects.filter(fin_prdt_cd=option.get('fin_prdt_cd')).first()
        if product:
            DepositOption.objects.update_or_create(
                deposit_product=product,
                intr_rate_type=option.get('intr_rate_type'),
                save_trm=option.get('save_trm'),
                defaults={
                    'intr_rate_type_nm': option.get('intr_rate_type_nm'),
                    'intr_rate': _to_decimal(option.get('intr_rate')),
                    'intr_rate2': _to_decimal(option.get('intr_rate2')),
                }
            )
    return True

@transaction.atomic
def save_saving_products():
    """적금 상품 목록을 API로부터 받아와 데이터베이스에 저장합니다."""
    url = f'{BASE_URL}/savingProductsSearch.json'
    params = {'auth': API_KEY, 'topFinGrpNo': '020000', 'pageNo': 1}
    data = _fetch_financial_products(url, params)

    if not data or 'result' not in data:
        return False

    base_list = data['result'].get('baseList', [])
    option_list = data['result'].get('optionList', [])

    for base in base_list:
        product, created = SavingProduct.objects.update_or_create(
            fin_prdt_cd=base.get('fin_prdt_cd'),
            defaults={
                'dcls_month': base.get('dcls_month'),
                'fin_co_no': base.get('fin_co_no'),
                'kor_co_nm': base.get('kor_co_nm'),
                'fin_prdt_nm': base.get('fin_prdt_nm'),
                'join_way': base.get('join_way'),
                'mtrt_int': base.get('mtrt_int'),
                'spcl_cnd': base.get('spcl_cnd'),
                'join_deny': base.get('join_deny'),
                'join_member': base.get('join_member'),
                'etc_note': base.get('etc_note'),
                'max_limit': _to_decimal(base.get('max_limit')),
            }
        )

    for option in option_list:
        product = SavingProduct.objects.filter(fin_prdt_cd=option.get('fin_prdt_cd')).first()
        if product:
            SavingOption.objects.update_or_create(
                saving_product=product,
                intr_rate_type=option.get('intr_rate_type'),
                rsrv_type=option.get('rsrv_type'),
                save_trm=option.get('save_trm'),
                defaults={
                    'intr_rate_type_nm': option.get('intr_rate_type_nm'),
                    'rsrv_type_nm': option.get('rsrv_type_nm'),
                    'intr_rate': _to_decimal(option.get('intr_rate')),
                    'intr_rate2': _to_decimal(option.get('intr_rate2')),
                }
            )
    return True 