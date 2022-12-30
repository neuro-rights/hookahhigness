from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web3_auth.urls')),
    #path('web3_auth/', include('web3_auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    #path('auth/', include('django.contrib.auth.urls')),
]