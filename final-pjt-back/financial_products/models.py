from django.db import models

# Create your models here.
from django.conf import settings

class DepositProduct(models.Model):
    interest_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interest_deposit', blank=True)
    dcls_month = models.TextField()
    fin_prdt_cd = models.TextField(unique=True)
    fin_co_no = models.TextField()
    kor_co_nm = models.TextField()
    fin_prdt_nm = models.TextField()
    join_way = models.TextField()
    mtrt_int = models.TextField()
    spcl_cnd = models.TextField()
    join_deny = models.IntegerField(default=0)
    join_member = models.TextField()
    etc_note = models.TextField(blank=True)
    max_limit = models.IntegerField(blank=True, null=True)

class SavingProduct(models.Model):
    interest_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interest_saving', blank=True)
    dcls_month = models.TextField()
    fin_prdt_cd = models.TextField(unique=True)
    fin_co_no = models.TextField()
    kor_co_nm = models.TextField()
    fin_prdt_nm = models.TextField()
    join_way = models.TextField()
    mtrt_int = models.TextField()
    spcl_cnd = models.TextField()
    join_deny = models.IntegerField(default=0)
    join_member = models.TextField()
    etc_note = models.TextField(blank=True)
    max_limit = models.IntegerField(blank=True, null=True)

class DepositOption(models.Model):
    # fin_prdt_cd = models.IntegerField()
    deposit_product = models.ForeignKey(DepositProduct, on_delete=models.CASCADE, related_name='options')
    intr_rate_type = models.CharField(max_length=100)
    intr_rate_type_nm = models.CharField(max_length=100)    
    save_trm = models.IntegerField(default=0)
    intr_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    intr_rate2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)

class SavingOption(models.Model):
    # fin_prdt_cd = models.IntegerField()
    saving_product = models.ForeignKey(SavingProduct, on_delete=models.CASCADE, related_name='options')
    intr_rate_type = models.CharField(max_length=100)
    intr_rate_type_nm = models.CharField(max_length=100)
    rsrv_type = models.TextField()
    rsrv_type_nm = models.TextField()
    save_trm = models.IntegerField()
    intr_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    intr_rate2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)