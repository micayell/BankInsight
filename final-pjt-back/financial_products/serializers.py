from rest_framework import serializers
from .models import DepositProduct, DepositOption, SavingProduct, SavingOption

class DepositOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOption
        fields = ['id', 'intr_rate_type_nm', 'save_trm', 'intr_rate', 'intr_rate2'] 

class SavingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingOption
        fields = ['id', 'intr_rate_type_nm', 'rsrv_type_nm', 'save_trm', 'intr_rate', 'intr_rate2'] 

class InterestDepositSerializer(serializers.ModelSerializer):
    options = DepositOptionSerializer(many=True, read_only=True)
    class Meta:
        model = DepositProduct
        fields = (
            'id', 
            'fin_prdt_cd', 
            'fin_prdt_nm', 
            'kor_co_nm', 
            'mtrt_int',
            'options'
        )

class InterestSavingSerializer(serializers.ModelSerializer):
    options = SavingOptionSerializer(many=True, read_only=True)
    class Meta:
        model = SavingProduct
        fields = (
            'id',
            'fin_prdt_cd', 
            'fin_prdt_nm', 
            'kor_co_nm', 
            'mtrt_int', 
            'options'
        )

class DepositListSerializer(serializers.ModelSerializer):
    options = DepositOptionSerializer(many=True, read_only=True)

    class Meta:
        model = DepositProduct
        fields = [
            'id', 
            'fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm', 
            'join_way', 'etc_note', 'mtrt_int', 'options',
        ]
        read_only_fields = ('interest_user',)

class DepositDetailSerializer(serializers.ModelSerializer):
    options = DepositOptionSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField() 

    class Meta:
        model = DepositProduct
        fields = '__all__'
        read_only_fields = ('interest_user',)

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return obj.interest_user.filter(pk=request.user.pk).exists()
        return False

class SavingListSerializer(serializers.ModelSerializer):
    options = SavingOptionSerializer(many=True, read_only=True)
    class Meta:
        model = SavingProduct
        fields = [
            'id', 
            'fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm', 
            'join_way', 'etc_note', 'mtrt_int', 'options',
        ]
        read_only_fields = ('interest_user',)

class SavingDetailSerializer(serializers.ModelSerializer):
    options = SavingOptionSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField() 

    class Meta:
        model = SavingProduct
        fields = '__all__'
        read_only_fields = ('interest_user',)

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            return obj.interest_user.filter(pk=request.user.pk).exists()
        return False

class DepositMonthSerializer(serializers.ModelSerializer):
    options = DepositOptionSerializer(many=True, read_only=True)
    class Meta:
        model = DepositProduct
        fields = '__all__' 
        read_only_fields = ('interest_user',)

    def __init__(self, *args, **kwargs):
        self.save_trm = kwargs.pop('save_trm', None)
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        options_data = representation.pop('options') 

        if self.save_trm is not None and isinstance(options_data, list) :
            filtered_options = [option for option in options_data if option.get('save_trm') == self.save_trm]
            representation['options'] = filtered_options
        else:
            representation['options'] = options_data
        return representation
     
class SavingMonthSerializer(serializers.ModelSerializer):
    options = SavingOptionSerializer(many=True, read_only=True)
    class Meta:
        model = SavingProduct
        fields = ('id', 'dcls_month', 'fin_prdt_cd', 'fin_co_no', 
                  'kor_co_nm', 'fin_prdt_nm', 'join_way', 'mtrt_int', 
                  'spcl_cnd', 'join_deny', 'join_member', 'etc_note', 
                  'max_limit', 'options') 
        read_only_fields = ('interest_user',)

    def __init__(self, *args, **kwargs):
        self.save_trm = kwargs.pop('save_trm', None)
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        options_data = representation.pop('options') 

        if self.save_trm is not None and isinstance(options_data, list) :
            filtered_options = [option for option in options_data if option.get('save_trm') == self.save_trm]
            representation['options'] = filtered_options
        else:
            representation['options'] = options_data
        return representation
    
# class DepositRecommendSerializer(serializers.ModelSerializer): 
#     options = DepositOptionSerializer(many=True, read_only=True)
#     class Meta:
#         model = DepositProduct
#         fields = '__all__'

# class SavingRecommendSerializer(serializers.ModelSerializer): 
#     options = SavingOptionSerializer(many=True, read_only=True)
#     class Meta:
#         model = SavingProduct
#         fields = '__all__'