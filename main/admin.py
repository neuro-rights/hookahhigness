from django.contrib import admin
from .models import NFT, NFTCollection, Photo, Sell, Bid, Purchase

# Register your models here.
admin.site.register(NFT)
admin.site.register(Photo)
admin.site.register(NFTCollection)
admin.site.register(Sell)
admin.site.register(Bid)
admin.site.register(Purchase)
