from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    nickname = models.CharField(max_length=20)
    REQUIRED_FIELDS = ["nickname"]

    age = models.IntegerField(default=0)
    profile_img = models.ImageField(
        upload_to="images/", default="images/default_profile.jpg"
    )
    salary = models.IntegerField(default=0)
    wealth = models.IntegerField(default=0)
    tendency = models.IntegerField(default=0)
    desirePeriod = models.IntegerField(default=0)

    subscribed_products = models.JSONField(
        "가입한 상품목록",
        default=list,
        blank=True,
        help_text='상품 코드(ID) 리스트로 저장 (예: ["DP0001", "SV0003"])',
    )

