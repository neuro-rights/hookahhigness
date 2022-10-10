from datetime import datetime, timedelta, time

from django.shortcuts import render

from .models import Collection

from .parts.utils.pagination import *
from .parts.utils.form_kwargs import *
from .parts.auth.functions import *
from .parts.assets.classes import *
from .parts.assets.functions import *
from .parts.collections.classes import *
from .parts.collections.functions import *
from .parts.bids.classes import *
from .parts.bids.functions import *
from .parts.auctions.classes import *
from .parts.auctions.functions import *
from .parts.purchases.classes import *
from .parts.raffles.classes import *
from .parts.raffles.functions import *

# from .view_parts.opensea.opensea import *
from .parts.market.classes import *
from .parts.market.functions import *



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
