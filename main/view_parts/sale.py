# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

#
from ..forms import BidForm, SellForm
from ..models import NFT, NFTCollection, Photo, Sell, Bid

#
from ..utils.nft import NFTUtils
from ..utils.contract import ContractUtils
from .pagination import *

#
import pprint
import uuid
import requests
from requests import HTTPError
import json
import os
from pathlib import Path
import sys
import logging


def all_for_sale(request):
    #
    sell_list = Sell.objects.order_by("-id").all()
    context = {"page_obj": get_page_obj(request, sell_list, 25)}
    return render(request, "nfts/for_sale.html", context)


@login_required
def accept_bid(request, bid_id):
    #
    try:
        #
        contract_address = os.environ["CONTRACT_ADDRESS"]
        contract_abi = os.environ["CONTRACT_ABI"]
        #
        bid = Bid.objects.get(id=bid_id)
        nft_metadata_uri = bid.nft.metadata_uri
        user_wallet = Profile.object.select_related("user").get(user=bid.bidder).wallet_address
        #
        nftutils = NFTUtils()
        bc_setup = nftutils.set_up_blockchain(contract=contract_address, abi_path=contract_abi)
        tx_hash, tx_token_id = nftutils.web3_mint(userAddress=user_wallet, tokenURI=nft_metadata_uri, eth_json=bc_setup)
        #
        new_purchase = Purchase(commit=False)
        new_purchase.bid_id = bid_id
        new_purchase.tx_hash = tx_hash
        new_purchase.tx_token_id = tx_token_id
        new_purchase.save()
        #
    except Exception as err:
        #
        print("Purchase of NFT failed: {}".format(err))
        return redirect("nft_detail", nft_id=bid.nft_id)
    #
    return redirect("nft_detail", nft_id=bid.nft_id)


@login_required
def reject_bid(request, bid_id):
    #
    bid = Bid.objects.get(id=bid_id)
    bid_nft_id = bid.nft.id
    try:
        #
        bid.delete()
        #
    except Exception as err:
        #
        print("Failed to delete Bid: {}".format(err))
    #
    return redirect("nft_detail", nft_id=bid_nft_id)


@login_required
def add_bid(request, nft_id):
    #
    form = BidForm(request.POST)
    sale = Sell.objects.select_related("nft").get(id=nft_id)
    #
    if not form.is_valid():
        return redirect("nft_detail", nft_id=nft_id)
    #
    new_bid = form.save(commit=False)
    if new_bid.bid_price <= sale.min_bid_price:
        return redirect("nft_detail", nft_id=nft_id)
    #
    sale.min_bid_price = new_bid.bid_price
    sale.save()
    #
    new_bid.nft_id = nft_id
    new_bid.bidder_id = request.user.id
    new_bid.save()
    #
    return redirect("nft_detail", nft_id=nft_id)


@login_required
def sell(request, nft_id):
    #
    form = SellForm(request.POST)
    if form.is_valid():
        new_sell = form.save(commit=False)
        new_sell.nft_id = nft_id
        new_sell.save()
        return redirect("nft_detail", nft_id=nft_id)
    #
    context = {"nft": nft_id, "form": form}
    return render(request, "main/sell_form.html", context)
