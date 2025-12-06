import requests
from django.conf import settings
from decimal import Decimal, InvalidOperation
from .models import ProductPrice, SilverPrice
from .scraper import scrape_silver

# 1) 금 시세 API URL
GOLD_API_URL = 'https://apis.data.go.kr/1160100/service/GetGeneralProductInfoService/getGoldPriceInfo'

def fetch_gold_data(api_key: str, start: str, end: str):
    params = {
        'serviceKey': api_key,
        'resultType': 'json',
        'pageNo': 1,
        'numOfRows': 1000,
    }
    if start:
        # API는 YYYYMMDD 포맷 요구
        params['beginBasDt'] = start.replace('-', '')
    if end:
        params['endBasDt'] = end.replace('-', '')

    resp = requests.get(GOLD_API_URL, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json()['response']['body']['items']['item']
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
            # Handle cases where conversion to Decimal fails for a record
            print(f"Could not convert data to Decimal for date {date}, skipping record. Data: {item}")
            continue

def fetch_silver_data(start: str, end: str):
    """
    scrape_silver(start, end)로부터 반환된 리스트를
    SilverPrice 테이블에 update_or_create 합니다.
    """
    from .scraper import scrape_silver

    data = scrape_silver(start, end) 
    if not data:
        return
    for rec in data:
        SilverPrice.objects.update_or_create(
            date=rec['date'],
            defaults={'sell_price_per_gram': rec['price']}
        )