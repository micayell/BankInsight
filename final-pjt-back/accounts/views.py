from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import (
    UserPageSerializer,
    UserInfoChangeSerializer,
)
from financial_products.models import DepositProduct, SavingProduct 
from django.core.mail import send_mail
from django.core.cache import cache
import random
import string
from rest_framework.permissions import AllowAny

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated]) 
def user_profile(request, username):
    target_user = get_object_or_404(get_user_model(), username=username)

    if request.method == "GET":
        if request.user == target_user or request.user.is_staff:
            serializer = UserPageSerializer(target_user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "You are not authorized to view this profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
    elif request.method == "PUT":
        if request.user != target_user:
            return Response(
                {"error": "You can only edit your own profile."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UserInfoChangeSerializer(target_user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save() 
            updated_user_serializer = UserPageSerializer(target_user, context={'request': request})
            return Response(updated_user_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_interest(request):
    user = request.user
    for code in user.subscribed_products or []:
        if not isinstance(code, str): 
            continue
        if code.startswith("DP"): 
            try:
                dp = DepositProduct.objects.get(fin_prdt_cd=code)
                dp.interest_user.add(user)
            except DepositProduct.DoesNotExist:
                continue
        elif code.startswith("SV"): 
            try:
                sp = SavingProduct.objects.get(fin_prdt_cd=code)
                sp.interest_user.add(user)
            except SavingProduct.DoesNotExist:
                continue
    return JsonResponse(
        {"message": "Interest products updated based on subscriptions."}, status=status.HTTP_200_OK
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def user_delete(request, username):
    target_user = get_object_or_404(get_user_model(), username=username)
    if request.user != target_user:
        return Response({"error": "Unauthorized. You can only delete your own account."}, status=status.HTTP_403_FORBIDDEN)
    target_user.delete() 
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_email_code(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': '이메일을 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
    
    User = get_user_model()
    if User.objects.filter(email=email).exists():
        return Response({'error': '이미 가입된 이메일입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
    code = ''.join(random.choices(string.digits, k=6))
    
    # 캐시에 3분간 저장 (key: 이메일, value: 인증번호)
    cache.set(f'email_code_{email}', code, timeout=180)
    
    try:
        send_mail(
            subject='[BankInsight] 회원가입 이메일 인증번호',
            message=f'인증번호 6자리: \n\n {code} \n\n 3분 안에 입력해주세요.',
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': '인증번호가 발송되었습니다.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_code(request):
    email = request.data.get('email')
    code = request.data.get('code')
    
    if not email or not code:
        return Response({'error': '이메일과 인증번호를 모두 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        
    saved_code = cache.get(f'email_code_{email}')
    if not saved_code:
        return Response({'error': '인증번호가 만료되었거나 이메일이 잘못되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
    if saved_code == str(code):
        cache.set(f'email_verified_{email}', True, timeout=1800)
        return Response({'message': '인증 성공'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': '인증번호가 일치하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
