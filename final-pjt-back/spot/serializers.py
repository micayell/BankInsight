from rest_framework import serializers
from .models import ProductPrice, OilPrice

class GoldPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = '__all__'

class OilPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OilPrice
        fields = ['date', 'price', 'last_updated']

class GoldPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ['date', 'price']

class OilPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OilPrice
        fields = ['date', 'price']
