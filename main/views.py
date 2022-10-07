from datetime import datetime, timedelta, time

from django.shortcuts import render

from .models import Asset

from .parts.utils.pagination import *
from .parts.utils.form_kwargs import *
from .parts.auth.auth_functions import *
from .parts.nfts.nft_classes import *
from .parts.nfts.nft_functions import *
from .parts.assets.asset_classes import *
from .parts.assets.asset_functions import *
from .parts.bids.bid_classes import *
from .parts.bids.bid_functions import *
from .parts.auctions.auction_classes import *
from .parts.auctions.auction_functions import *
from .parts.purchases.purchase_classes import *
from .parts.raffles.raffle_classes import *
from .parts.raffles.raffle_functions import *

# from .view_parts.opensea.opensea import *
from .parts.market.market_classes import *
from .parts.market.market_functions import *



class HomeView(PassArgumentsToForm, ListView):
    paginate_by = 25
    model = Auction
    form_class = AuctionForm
    template_name = "home.html"

    def get_queryset(self):
        now = datetime.now()
        return Auction.objects.filter(datetime_start__lte=now, datetime_end__gte=now)

def home(request):
    #
    auctions_list = Auction.objects.order_by("-id").all()
    context = {"page_obj": get_page_obj(request, auctions_list, 25)}
    return render(request, "home.html", context)


def opensea(request):
    pass


def tickets(request):
    pass


def about(request):
    pass


def help(request):
    return render(request, 'help/index.html')

def room(request, room_name):
    return render(request, 'help/room.html', {
        'room_name': room_name
    })
