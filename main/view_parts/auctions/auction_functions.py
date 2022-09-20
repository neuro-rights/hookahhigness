# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core import serializers
#
from ...forms import BidForm
from ...models import Auction

#
from ..utils.pagination import *


@login_required
def auction_detail(request, auction_uuid):
    #
    auction = Auction.objects.get(uuid=auction_uuid)
    bid_form = BidForm()
    #
    return render(
        request, "auctions/detail.html", {"auction": auction, "bid_form": bid_form}
    )


@login_required
def auctions_own(request):
    #
    auctions_own = Auction.objects.filter(seller=request.user)
    #
    context = {"page_obj": get_page_obj(request, auctions_own, 25)}
    return render(request, "auctions/list.html", context)


@login_required
def auctions_running(request):
    #
    auctions_running = Auction.objects.all()
    #
    context = {"page_obj": get_page_obj(request, auctions_running, 25)}
    return render(request, "auctions/list.html", context)


@login_required
def auctions_own_running(request):
    #
    auctions_own_running = Auction.objects.all()
    #
    context = {"page_obj": get_page_obj(request, auctions_own_running, 25)}
    return render(request, "auctions/list.html", context)


@login_required
def auctions_own_scheduled(request):
    #
    auctions_own_scheduled = Auction.objects.all()
    #
    context = {"page_obj": get_page_obj(request, auctions_own_scheduled, 25)}
    return render(request, "auctions/list.html", context)


@login_required
def auctions_own_ended(request):
    #
    auctions_own_ended = Auction.objects.all()
    #
    context = {"page_obj": get_page_obj(request, auctions_own_ended, 25)}
    return render(request, "auctions/list.html", context)


@login_required
def auction_add_assets(request, auction_uuid):
    pass


@login_required
def auction_add_bid(request, auction_uuid):
     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        import logging
        logging.basicConfig(filename='mylog.log', level=logging.DEBUG)
        logging.debug('request.method=POST')
        form = BidForm(request.POST)
        logging.debug('errors=%s', form.errors)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            auction = Auction.objects.get(uuid=auction_uuid)
            new_bid = form.save(commit=False)
            if new_bid.value <= auction.bid_current_value:
                return render(
                    request, "auctions/detail.html", {"auction": auction, "bid_form": form}
                )
            #
            new_bid.value = float(request.POST["value"])
            new_bid.buyer = request.user
            new_bid.auction = auction
            new_bid.save()
            #
            auction.bid_current_value = new_bid.value
            auction.save()
            # redirect to a new URL:
            return render(
                request, "auctions/detail.html", {"auction": auction, "bid_form": form}
            )
            # ...
        else:
            print(form.errors)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = BidForm()
        return render(
            request, "auctions/detail.html", {"auction": auction, "bid_form": bid_form}
        )


def auction_bids(request):
    pass
