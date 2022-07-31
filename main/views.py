from django.shortcuts import render

from .models import Asset

from .view_parts.utils.pagination import *
from .view_parts.utils.form_kwargs import *
from .view_parts.auth.auth_functions import *
from .view_parts.nfts.nft_classes import *
from .view_parts.nfts.nft_functions import *
from .view_parts.assets.asset_classes import *
from .view_parts.assets.asset_functions import *
from .view_parts.bids.bid_classes import *
from .view_parts.bids.bid_functions import *
from .view_parts.auctions.auction_classes import *
from .view_parts.auctions.auction_functions import *
from .view_parts.purchases.purchase_classes import *
from .view_parts.raffles.raffle_classes import *
from .view_parts.raffles.raffle_functions import *

# from .view_parts.opensea.opensea import *
from .view_parts.market.market_classes import *
from .view_parts.market.market_functions import *


def home(request):
    #
    auctions_list = Auction.objects.order_by("-id").all()
    context = {"page_obj": get_page_obj(request, auctions_list, 25)}
    return render(request, "home.html", context)
