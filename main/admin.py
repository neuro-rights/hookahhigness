from django.contrib import admin
from .models import User, Asset, Collection, Auction, Raffle, Bid, Purchase

# Register your models here.
#admin.site.register(User)
admin.site.register(Asset)
admin.site.register(Collection)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Purchase)
admin.site.register(Raffle)
