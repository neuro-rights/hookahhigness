# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

#
from ..utils.pagination import *

#
from ...models import Auction


def market_list(request):
    #
    auctions_list = Auction.objects.order_by("-id").all()
    context = {"page_obj": get_page_obj(request, auctions_list, 25)}
    return render(request, "market/list.html", context)


@login_required
def market_own(request):
    #
    auctions_own = Auction.objects.order_by("-id").filter(creator=request.user)
    context = {"page_obj": get_page_obj(request, auctions_own, 25)}
    return render(request, "market/list.html", context)
