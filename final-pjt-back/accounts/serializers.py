from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import (
    LoginSerializer,
    TokenSerializer,
    TokenModel,
    UserDetailsSerializer,
)
from django.contrib.auth import get_user_model
from allauth.account.adapter import get_adapter
from financial_products.models import DepositProduct, SavingProduct
from financial_products.serializers import InterestDepositSerializer, InterestSavingSerializer

class CustomRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(max_length=20, required=True, allow_blank=False)
    email = serializers.EmailField(required=True)
    age = serializers.IntegerField(required=True)
    salary = serializers.IntegerField(required=True)
    wealth = serializers.IntegerField(required=True)
    tendency = serializers.IntegerField(required=True)
    desirePeriod = serializers.IntegerField(required=True)

    
    def validate_email(self, value):
        if not cache.get(f'email_verified_{value}'):
            raise ValidationError('이메일 인증을 먼저 완료해주세요.')
        return value

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update(
            {
                "nickname": self.validated_data.get("nickname", ""),
                "age": self.validated_data.get("age", 0),
                "salary": self.validated_data.get("salary", 0),
                "wealth": self.validated_data.get("wealth", 0),
                "tendency": self.validated_data.get("tendency", 0),
                "desirePeriod": self.validated_data.get("desirePeriod", 0),
            }
        )
        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        user.nickname = self.cleaned_data.get("nickname")
        user.age = self.cleaned_data.get("age")
        user.salary = self.cleaned_data.get("salary")
        user.wealth = self.cleaned_data.get("wealth")
        user.tendency = self.cleaned_data.get("tendency")
        user.desirePeriod = self.cleaned_data.get("desirePeriod")
        user.save()
        return user


class CustomLoginSerializer(LoginSerializer):
    # email = None
    pass


class CustomUserDetailSerializer(UserDetailsSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "nickname",
            "age",
            "salary",
            "wealth",
            "tendency",
            "desirePeriod",
            "subscribed_products", 
        )

class CustomTokenSerializer(TokenSerializer):
    user = CustomUserDetailSerializer(read_only=True)

    class Meta:
        model = TokenModel
        fields = ("key", "user")

class UserPageSerializer(serializers.ModelSerializer):
    interested_deposits = InterestDepositSerializer(source='interest_deposit', many=True, read_only=True)
    interested_savings = InterestSavingSerializer(source='interest_saving', many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "nickname",
            "age",
            "salary",
            "wealth",
            "tendency",
            "desirePeriod",
            "profile_img",
            "subscribed_products",      
            "interested_deposits",       
            "interested_savings",        
        )
        read_only_fields = ("id", "username", "email")

class UserInfoChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "nickname",
            "age",
            "profile_img",
            "salary",
            "wealth",
            "tendency",
            "desirePeriod",
        )

class UserGetInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id",)

class NewInfoChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "nickname",
            "age",
            "profile_img",
            "salary",
            "wealth",
            "tendency",
            "desirePeriod",
        )

class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("subscribed_products",)