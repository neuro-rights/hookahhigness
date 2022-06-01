from django.contrib import admin
from .models import NFT, NFTCollection, Photo, Bid, Purchase

# Register your models here.
admin.site.register(NFTCollection)
admin.site.register(NFT)
admin.site.register(Photo)
admin.site.register(Bid)
admin.site.register(Purchase)
