from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import DepositProduct, DepositOption, SavingProduct, SavingOption
from .serializers import (
    DepositListSerializer, DepositDetailSerializer, DepositOptionSerializer,
    SavingListSerializer,  SavingDetailSerializer,  SavingOptionSerializer,
)
from . import services

@api_view(['POST']) 
@permission_classes([AllowAny])
def load_deposit_products(request): 
    """외부 API로부터 정기예금 상품 목록을 로드하여 데이터베이스에 저장합니다."""
    if services.save_deposit_products():
        return Response({'detail': '정기예금 상품 정보 로드 성공'}, status=status.HTTP_201_CREATED)
    return Response({'detail': '금융 API 호출 실패 또는 데이터 처리 오류'}, status=status.HTTP_502_BAD_GATEWAY)

@api_view(['POST']) 
@permission_classes([AllowAny])
def load_saving_products(request): 
    """외부 API로부터 적금 상품 목록을 로드하여 데이터베이스에 저장합니다."""
    if services.save_saving_products():
        return Response({'detail': '적금 상품 정보 로드 성공'}, status=status.HTTP_201_CREATED)
    return Response({'detail': '금융 API 호출 실패 또는 데이터 처리 오류'}, status=status.HTTP_502_BAD_GATEWAY)

@api_view(['GET'])
@permission_classes([AllowAny])
def deposit_product_list(request):
    """전체 정기예금 상품 목록을 반환합니다."""
    # if not DepositProduct.objects.exists():
    #     services.save_deposit_products()

    products   = DepositProduct.objects.prefetch_related('options', 'interest_user').all()
    serializer = DepositListSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def deposit_detail(request, fin_prdt_cd):
    product = get_object_or_404(DepositProduct, fin_prdt_cd=fin_prdt_cd)
    serializer = DepositDetailSerializer(product, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_deposit(request, fin_prdt_cd):
    product = get_object_or_404(DepositProduct, fin_prdt_cd=fin_prdt_cd)
    user = request.user
    if product.interest_user.filter(id=user.id).exists():
        product.interest_user.remove(user)
        return Response({'status': 'unliked', 'message': '관심 상품에서 제외되었습니다.', 'is_liked': False})
    product.interest_user.add(user)
    return Response({'status': 'liked', 'message': '관심 상품으로 등록되었습니다.', 'is_liked': True})

@api_view(['GET'])
@permission_classes([AllowAny])
def bank_deposit(request, bank_name):
    products = DepositProduct.objects.filter(kor_co_nm__icontains=bank_name)
    if not products.exists():
        return Response({'detail': '해당 은행의 상품이 없습니다.'},
                        status=status.HTTP_204_NO_CONTENT)
    serializer = DepositDetailSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def saving_product_list(request):
    """전체 적금 상품 목록을 반환합니다."""
    # if not SavingProduct.objects.exists():
    #     services.save_saving_products()

    products   = SavingProduct.objects.prefetch_related('options', 'interest_user').all()
    serializer = SavingListSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def saving_detail(request, fin_prdt_cd):
    product = get_object_or_404(SavingProduct, fin_prdt_cd=fin_prdt_cd)
    serializer = SavingDetailSerializer(product, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_saving(request, fin_prdt_cd):
    product = get_object_or_404(SavingProduct, fin_prdt_cd=fin_prdt_cd)
    user = request.user
    if product.interest_user.filter(id=user.id).exists():
        product.interest_user.remove(user)
        return Response({'status': 'unliked', 'message': '관심 상품에서 제외되었습니다.', 'is_liked': False})
    product.interest_user.add(user)
    return Response({'status': 'liked', 'message': '관심 상품으로 등록되었습니다.', 'is_liked': True})

@api_view(['GET'])
@permission_classes([AllowAny])
def bank_saving(request, bank_name):
    products = SavingProduct.objects.filter(kor_co_nm__icontains=bank_name)
    if not products.exists():
        return Response({'detail': '해당 은행의 상품이 없습니다.'},
                        status=status.HTTP_204_NO_CONTENT)
    serializer = SavingDetailSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def deposit_option_list(request, fin_prdt_cd):
    product = get_object_or_404(DepositProduct, fin_prdt_cd=fin_prdt_cd)
    options = DepositOption.objects.filter(deposit_product=product)
    serializer = DepositOptionSerializer(options, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def deposit_option_detail(request, fin_prdt_cd, option_id):
    product = get_object_or_404(DepositProduct, fin_prdt_cd=fin_prdt_cd)
    option = get_object_or_404(
        DepositOption, deposit_product=product, id=option_id)
    serializer = DepositOptionSerializer(option)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def saving_option_list(request, fin_prdt_cd):
    product = get_object_or_404(SavingProduct, fin_prdt_cd=fin_prdt_cd)
    options = SavingOption.objects.filter(saving_product=product)
    serializer = SavingOptionSerializer(options, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def saving_option_detail(request, fin_prdt_cd, option_id):
    product = get_object_or_404(SavingProduct, fin_prdt_cd=fin_prdt_cd)
    option = get_object_or_404(
        SavingOption, saving_product=product, id=option_id)
    serializer = SavingOptionSerializer(option)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def load_mortgage_loan_products(request):
    if services.save_mortgage_loan_products(): return Response({'detail': '주택담보대출 상품 로드 성공'}, status=status.HTTP_201_CREATED)
    return Response({'detail': '외부 API 호출 오류'}, status=status.HTTP_502_BAD_GATEWAY)

@api_view(['POST'])
@permission_classes([AllowAny])
def load_jeonse_loan_products(request):
    if services.save_jeonse_loan_products(): return Response({'detail': '전세자금대출 상품 로드 성공'}, status=status.HTTP_201_CREATED)
    return Response({'detail': '외부 API 호출 오류'}, status=status.HTTP_502_BAD_GATEWAY)

@api_view(['GET'])
@permission_classes([AllowAny])
def mortgage_loan_list(request):
    from .models import MortgageLoanProduct
    from .serializers import MortgageLoanProductSerializer
    products = MortgageLoanProduct.objects.prefetch_related('options', 'interest_user').all()
    serializer = MortgageLoanProductSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def mortgage_loan_detail(request, fin_prdt_cd):
    from .models import MortgageLoanProduct
    from .serializers import MortgageLoanProductSerializer
    product = get_object_or_404(MortgageLoanProduct, fin_prdt_cd=fin_prdt_cd)
    serializer = MortgageLoanProductSerializer(product, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_mortgage_loan(request, fin_prdt_cd):
    from .models import MortgageLoanProduct
    product = get_object_or_404(MortgageLoanProduct, fin_prdt_cd=fin_prdt_cd)
    if product.interest_user.filter(id=request.user.id).exists():
        product.interest_user.remove(request.user)
        return Response({'status':'unliked', 'message':'관심 상품에서 제외되었습니다.', 'is_liked':False})
    product.interest_user.add(request.user)
    return Response({'status':'liked', 'message':'관심 상품으로 등록되었습니다.', 'is_liked':True})

@api_view(['GET'])
@permission_classes([AllowAny])
def jeonse_loan_list(request):
    from .models import JeonseLoanProduct
    from .serializers import JeonseLoanProductSerializer
    products = JeonseLoanProduct.objects.prefetch_related('options', 'interest_user').all()
    serializer = JeonseLoanProductSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def jeonse_loan_detail(request, fin_prdt_cd):
    from .models import JeonseLoanProduct
    from .serializers import JeonseLoanProductSerializer
    product = get_object_or_404(JeonseLoanProduct, fin_prdt_cd=fin_prdt_cd)
    serializer = JeonseLoanProductSerializer(product, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_jeonse_loan(request, fin_prdt_cd):
    from .models import JeonseLoanProduct
    product = get_object_or_404(JeonseLoanProduct, fin_prdt_cd=fin_prdt_cd)
    if product.interest_user.filter(id=request.user.id).exists():
        product.interest_user.remove(request.user)
        return Response({'status':'unliked', 'message':'관심 상품에서 제외되었습니다.', 'is_liked':False})
    product.interest_user.add(request.user)
    return Response({'status':'liked', 'message':'관심 상품으로 등록되었습니다.', 'is_liked':True})
