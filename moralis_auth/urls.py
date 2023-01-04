from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('accounts/', include('django.contrib.auth.urls')),
    path('', include('web3_auth.urls')),
    #path('web3_auth/', include('web3_auth.urls')),
]