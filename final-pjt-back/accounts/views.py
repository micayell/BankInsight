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