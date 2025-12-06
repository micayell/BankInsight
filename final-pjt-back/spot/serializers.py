from rest_framework import serializers
from .models import ProductPrice,SilverPrice

class GoldPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = '__all__'

class SilverPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SilverPrice
        fields = ['date', 'buy_price_per_don', 'sell_price_per_don', 'buy_price_per_gram', 'sell_price_per_gram', 'last_updated']

class GoldPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ['date', 'price']

class SilverPriceHistorySerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(source='sell_price_per_gram')
    class Meta:
        model = SilverPrice
        fields = ['date', 'price']