# spot/management/commands/update_silver_prices.py
from django.core.management.base import BaseCommand
from datetime import datetime # 날짜 문자열 파싱에 사용
from spot.models import SilverPrice
from spot.scraper import scrape_goldgold_silver_prices # 스크레이퍼 함수 import

class Command(BaseCommand):
    help = 'Scrapes silver prices from the new API (irena111.cafe24.com) and updates the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting silver price scraping from new API...'))
        
        # scrape_goldgold_silver_prices 함수는 이제 다음 형식의 리스트를 반환합니다:
        # [{'date': 'YYYY-MM-DD', 'buy_price_per_don': X, 'sell_price_per_don': Y, ...}, ...]
        daily_prices_list = scrape_goldgold_silver_prices() 

        if daily_prices_list is None: # 스크레이퍼에서 오류 발생 시 None 반환
            self.stdout.write(self.style.ERROR('Failed to scrape data: Scraper returned None.'))
            return
        
        if not daily_prices_list: # 빈 리스트는 데이터가 없지만 오류는 아님
            self.stdout.write(self.style.SUCCESS('No new price data found or returned by scraper.'))
            return

        updated_count = 0
        created_count = 0

        for price_data_dict in daily_prices_list:
            date_str = price_data_dict.get("date")
            if not date_str: # 날짜 정보가 없는 데이터는 건너뜀
                self.stdout.write(self.style.WARNING(f"Skipping record due to missing date: {price_data_dict}"))
                continue
            
            try:
                # 스크레이퍼에서 이미 'YYYY-MM-DD' 형식의 문자열로 날짜를 제공
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                self.stdout.write(self.style.WARNING(f"Invalid date format skipped in management command: {date_str}"))
                continue

            # DB 저장을 위한 데이터 준비 (값이 없을 경우 None으로)
            defaults_to_update = {
                'buy_price_per_don': price_data_dict.get('buy_price_per_don'),
                'sell_price_per_don': price_data_dict.get('sell_price_per_don'),
                'buy_price_per_gram': price_data_dict.get('buy_price_per_gram'),
                'sell_price_per_gram': price_data_dict.get('sell_price_per_gram'),
            }
            
            try:
                obj, created = SilverPrice.objects.update_or_create(
                    date=date_obj, # PK
                    defaults=defaults_to_update # 업데이트할 필드들
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating/creating record for date {date_str}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully processed silver prices. Created: {created_count}, Updated: {updated_count}'))