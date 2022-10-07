# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core import serializers
#
from ...utils.contract import ContractUtils

from ...forms import BidForm
from ...models import Auction

#
from ..utils.pagination import *

from web3 import Web3

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
def auctions_own_running(request):
    #
    return render(request, "auctions/list_running.html")


@login_required
def auctions_own_scheduled(request):
    #
    return render(request, "auctions/list_scheduled.html")


@login_required
def auctions_own_ended(request):
    #
    return render(request, "auctions/list_ended.html")


@login_required
def auction_add_assets(request, auction_uuid):
    pass

def auction_deploy_contract(request, auction_uuid):
    """ """

    auction = Auction.objects.get(uuid=auction_uuid)
     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        contract_utils = ContractUtils()
        contract_utils.compile_contract()
        contract_utils.deploy_contract()
        contract_utils.verify_contract()
        return redirect(auction)


@login_required
def auction_add_bid(request, auction_uuid):
    """ """

    auction = Auction.objects.get(uuid=auction_uuid)
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
            new_bid = form.save(commit=False)
            if new_bid.value <= auction.bid_current_value:
                return redirect(auction)
            #
            new_bid.value = float(request.POST["value"])
            new_bid.buyer = request.user
            new_bid.auction = auction
            new_bid.save()
            #
            auction.bid_current_value = new_bid.value
            auction.save()
            # redirect to a new URL:
            return redirect(auction)
        else:
            print(form.errors)

    # if a GET (or any other method) we'll create a blank form
    else:
        return redirect(auction)


def auction_bids(request):
    pass
