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

class OilPrice(models.Model):
    date = models.DateField(unique=True, primary_key=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="할인평균단가(wtAvgPrcDisc)")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "석유 시세"
        verbose_name_plural = "석유 시세 목록"
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.price}"
