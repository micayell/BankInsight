from django.db import models
from django.conf import settings

class DepositProduct(models.Model):
    interest_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interest_deposit', blank=True)
    dcls_month = models.CharField(max_length=10)
    fin_prdt_cd = models.CharField(max_length=100, unique=True)
    fin_co_no = models.CharField(max_length=100)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=200)
    join_way = models.CharField(max_length=200)
    mtrt_int = models.TextField()
    spcl_cnd = models.TextField()
    join_deny = models.IntegerField(default=0)
    join_member = models.TextField()
    etc_note = models.TextField(blank=True)
    max_limit = models.BigIntegerField(blank=True, null=True)

class SavingProduct(models.Model):
    interest_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interest_saving', blank=True)
    dcls_month = models.CharField(max_length=10)
    fin_prdt_cd = models.CharField(max_length=100, unique=True)
    fin_co_no = models.CharField(max_length=100)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=200)
    join_way = models.CharField(max_length=200)
    mtrt_int = models.TextField()
    spcl_cnd = models.TextField()
    join_deny = models.IntegerField(default=0)
    join_member = models.TextField()
    etc_note = models.TextField(blank=True)
    max_limit = models.BigIntegerField(blank=True, null=True)

class DepositOption(models.Model):
    deposit_product = models.ForeignKey(DepositProduct, on_delete=models.CASCADE, related_name='options')
    intr_rate_type = models.CharField(max_length=100)
    intr_rate_type_nm = models.CharField(max_length=100)    
    save_trm = models.IntegerField(default=0)
    intr_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    intr_rate2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)

class SavingOption(models.Model):
    saving_product = models.ForeignKey(SavingProduct, on_delete=models.CASCADE, related_name='options')
    intr_rate_type = models.CharField(max_length=100)
    intr_rate_type_nm = models.CharField(max_length=100)
    rsrv_type = models.CharField(max_length=100)
    rsrv_type_nm = models.CharField(max_length=100)
    save_trm = models.IntegerField()
    intr_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    intr_rate2 = models.DecimalField(max_digits=5, decimal_places=2, null=True)

class MortgageLoanProduct(models.Model):
    interest_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interest_mortgage', blank=True)
    dcls_month = models.CharField(max_length=10)
    fin_prdt_cd = models.CharField(max_length=100, unique=True)
    fin_co_no = models.CharField(max_length=100)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=200)
    join_way = models.CharField(max_length=200)
    loan_inci_expn = models.TextField(blank=True) # 부대비용
    erly_rpay_fee = models.TextField(blank=True) # 중도상환수수료
    dly_rate = models.TextField(blank=True) # 연체이율
    loan_lmt = models.TextField(blank=True) # 한도

class JeonseLoanProduct(models.Model):
    interest_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='interest_jeonse', blank=True)
    dcls_month = models.CharField(max_length=10)
    fin_prdt_cd = models.CharField(max_length=100, unique=True)
    fin_co_no = models.CharField(max_length=100)
    kor_co_nm = models.CharField(max_length=100)
    fin_prdt_nm = models.CharField(max_length=200)
    join_way = models.CharField(max_length=200)
    loan_inci_expn = models.TextField(blank=True)
    erly_rpay_fee = models.TextField(blank=True)
    dly_rate = models.TextField(blank=True)
    loan_lmt = models.TextField(blank=True)

class MortgageLoanOption(models.Model):
    product = models.ForeignKey(MortgageLoanProduct, on_delete=models.CASCADE, related_name='options')
    mrtg_type_nm = models.CharField(max_length=100)
    rpay_type_nm = models.CharField(max_length=100)
    lend_rate_type_nm = models.CharField(max_length=100)
    lend_rate_min = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    lend_rate_max = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    lend_rate_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True)

class JeonseLoanOption(models.Model):
    product = models.ForeignKey(JeonseLoanProduct, on_delete=models.CASCADE, related_name='options')
    rpay_type_nm = models.CharField(max_length=100)
    lend_rate_type_nm = models.CharField(max_length=100)
    lend_rate_min = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    lend_rate_max = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    lend_rate_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True)

