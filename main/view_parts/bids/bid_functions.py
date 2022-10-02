# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core import serializers
#
from ...utils.nft import NFTUtils
from ...utils.contract import ContractUtils

#
from ..utils.pagination import *

#
from ...forms import PurchaseForm, BidForm
from ...models import User, Bid, Purchase, Nft

from web3 import Web3
import requests
import json



@login_required
def bid_accept(request, bid_uuid):
    """ """

    bid = Bid.objects.get(uuid=bid_uuid)
    print(bid.uuid)
    bid_form = BidForm()
    #
    try:
        #
        contract_address = bid.auction.contract_address
        contract_abi = bid.auction.contract_abi 
        #
        user_wallet = request.user.ethereum_wallet_address 
        #

        config={
                'seller_infura_ethereum_project_id':bid.auction.seller.infura_ethereum_project_id,
                'seller_ethereum_wallet_address':bid.auction.seller.ethereum_wallet_address,
                'seller_ethereum_wallet_private_key':bid.auction.seller.ethereum_wallet_private_key,
                'network':bid.auction.network, 
                'auction_contract_address':bid.auction.contract_address, 
            }
        #
        contractutils = ContractUtils()
        bc_setup = contractutils.set_up_blockchain(config)
        print(bc_setup)
        #
        for asset in bid.auction.assets.all():
            print(asset)
            for nft in asset.nfts.all():
                print(nft)
                #mint_nft(request=request, nft_uuid=nft.uuid)
                wallet_address = "0x2BBF135e8E7D2aA3eF1Ab949548f4E4d8Fa7db16" #request.user.ethereum_wallet_address
                tx_hash, tx_token = contractutils.web3_mint(
                    userAddress=wallet_address,
                    tokenURI=nft.token_id,
                    eth_json=bc_setup,
                )
                new_purchase = Purchase(commit=False)
                #new_purchase.bid_id = bid_id
                #new_purchase.tx_hash = tx_hash
                #new_purchase.tx_token = tx_token
                new_purchase.save()
        #
    except Exception as err:
        #
        print("Purchase of NFT failed: {}".format(err))
    #
    return render(
        request, "auctions/detail.html", {"auction": bid.auction, "bid_form": bid_form}
    )


@login_required
def bid_reject(request, bid_id):
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
def dafuq(request, bid_id):
    #
    bid = Bid.objects.get(id=bid_id)
    form = PurchaseForm(request.POST)
    #
    if form.is_valid():
        new_purchase = form.save(commit=False)
        new_purchase.bid_id = bid_id
        new_purchase.save()
        return redirect("auction_detail", auction_id=bid.auction_id)
    #
    context = {"bid": bid_id, "form": form}
    return render(request, "main/purchase_form.html", context)
