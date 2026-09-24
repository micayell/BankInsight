from django.contrib import admin
from django.urls import path, include
from django.conf import settings  
from django.conf.urls.static import static  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('accounts/allauth/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('articles/', include('articles.urls')),
    path('exchange/', include('exchange.urls')),
    path('financial-products/', include('financial_products.urls')),
    path('spot/', include('spot.urls')),
    path('api/v1/chatbot/', include('chatbot.urls')),
    path('api/v1/kftc/', include('kftc.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
