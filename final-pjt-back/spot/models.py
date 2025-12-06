from django.db import models

class ProductPrice(models.Model):
    # prodSeCode
    GOLD_CODE   = '04020000'
    SILVER_CODE = '04030000'
    PROD_CHOICES = [
        (GOLD_CODE,   '금 99.99_1Kg'),
        (SILVER_CODE, '은 99.99_1Kg'),
    ]

    prod_code    = models.CharField(max_length=20, choices=PROD_CHOICES)
    date         = models.DateField()
    price        = models.DecimalField(max_digits=12, decimal_places=2, help_text="종가")
    change_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, help_text="전일대비 등락값")
    change_rate  = models.DecimalField(max_digits=5, decimal_places=2, null=True, help_text="전일대비 등락률(%)")
    open_price   = models.DecimalField(max_digits=12, decimal_places=2, null=True, help_text="시가")
    high_price   = models.DecimalField(max_digits=12, decimal_places=2, null=True, help_text="고가")
    low_price    = models.DecimalField(max_digits=12, decimal_places=2, null=True, help_text="저가")
    trade_volume = models.DecimalField(max_digits=20, decimal_places=2, null=True, help_text="거래량")

    class Meta:
        unique_together = ('prod_code', 'date')
        ordering = ['prod_code', 'date']

    def __str__(self):
        return f"{self.get_prod_code_display()} @ {self.date}"

class SilverPrice(models.Model):
    date = models.DateField(unique=True, primary_key=True) # 날짜 (PK로 사용)
    buy_price_per_don = models.IntegerField(null=True, blank=True, help_text="내가 살때 가격 (원/3.75g)")
    sell_price_per_don = models.IntegerField(null=True, blank=True, help_text="내가 팔때 가격 (원/3.75g)")
    buy_price_per_gram = models.IntegerField(null=True, blank=True, help_text="내가 살때 가격 (원/g)")
    sell_price_per_gram = models.IntegerField(null=True, blank=True, help_text="내가 팔때 가격 (원/g)")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "은 시세"
        verbose_name_plural = "은 시세 목록"
        ordering = ['-date'] # 최신 날짜부터

    def __str__(self):
        return f"{self.date} - Buy: {self.buy_price_per_don}, Sell: {self.sell_price_per_don}"