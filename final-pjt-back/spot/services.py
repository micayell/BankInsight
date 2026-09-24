import requests
from django.conf import settings
from decimal import Decimal, InvalidOperation
from .models import ProductPrice, OilPrice

GOLD_API_URL = 'https://apis.data.go.kr/1160100/GetGeneralProductInfoService_V2/getGoldPriceInfo_V2'
OIL_API_URL = 'https://apis.data.go.kr/1160100/GetGeneralProductInfoService_V2/getOilPriceInfo_V2'

def fetch_gold_data(api_key: str, start: str, end: str):
    params = {
        'serviceKey': api_key,
        'resultType': 'json',
        'pageNo': 1,
        'numOfRows': 1000,
    }
    
    if start and end and start == end:
        params['basDt'] = start.replace('-', '')
    else:
        if start:
            params['beginBasDt'] = start.replace('-', '')
        if end:
            params['endBasDt'] = end.replace('-', '')

    resp = requests.get(GOLD_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    
    data_body = resp.json().get('response', {}).get('body', {})
    items_container = data_body.get('items') or {}
    items = items_container.get('item', []) if isinstance(items_container, dict) else []
    
    if not items:
        resp.status_code = 404
        raise requests.exceptions.HTTPError('No data found', response=resp)

    if isinstance(items, dict):
        items = [items]

    for item in items:
        d = item['basDt'] 
        date = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        try:
            ProductPrice.objects.update_or_create(
                prod_code=ProductPrice.GOLD_CODE,
                date=date,
                defaults={
                    'price':        Decimal(item.get('clpr', '0').replace(',', '')),
                    'open_price':   Decimal(item.get('mkp', '0').replace(',', '')),
                    'high_price':   Decimal(item.get('hipr', '0').replace(',', '')),
                    'low_price':    Decimal(item.get('lopr', '0').replace(',', '')),
                    'change_value': Decimal(item.get('vs', '0').replace(',', '')),
                    'change_rate':  Decimal(item.get('fltRt', '0').replace(',', '')),
                    'trade_volume': Decimal(item.get('trqu', '0').replace(',', '')),
                }
            )
        except InvalidOperation:
            print(f"Could not convert data to Decimal for date {date}, skipping record. Data: {item}")
            continue

def fetch_oil_data(api_key: str, start: str, end: str):
    params = {
        'serviceKey': api_key,
        'resultType': 'json',
        'pageNo': 1,
        'numOfRows': 1000,
    }
    if start and end and start == end:
        params['basDt'] = start.replace('-', '')
    else:
        if start:
            params['beginBasDt'] = start.replace('-', '')
        if end:
            params['endBasDt'] = end.replace('-', '')

    resp = requests.get(OIL_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    
    data_body = resp.json().get('response', {}).get('body', {})
    items_container = data_body.get('items') or {}
    items = items_container.get('item', []) if isinstance(items_container, dict) else []
    
    if not items:
        resp.status_code = 404
        raise requests.exceptions.HTTPError('No data found', response=resp)
        
    if isinstance(items, dict):
        items = [items]
        
    for item in items:
        d = item['basDt']
        date = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        try:
            OilPrice.objects.update_or_create(
                date=date,
                defaults={
                    'price': Decimal(item.get('wtAvgPrcDisc', '0').replace(',', ''))
                }
            )
        except InvalidOperation:
            continue
