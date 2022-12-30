# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core import serializers
#
from ...utils.asset import NFTUtils
from ...utils.contract import ContractUtils

#
from ..utils.pagination import *

#
from ...forms import PurchaseForm, BidForm
from ...models import User, Bid, Purchase, Asset

from web3 import Web3
import requests
import json



@login_required
def bid_accept(request, bid_uuid):
    """ """

    bid = Bid.objects.get(uuid=bid_uuid)
    bid_form = BidForm()
    #
    try:
        #
        contract_address = bid.auction.contract_address
        user_wallet = request.user.ethereum_wallet_address 

        config={
            'buyer_ethereum_wallet_address':bid.buyer.ethereum_wallet_address,
            'buyer_ethereum_wallet_private_key':bid.buyer.ethereum_wallet_private_key,
            'infura_ethereum_project_id':bid.auction.seller.infura_ethereum_project_id,
            'seller_ethereum_wallet_address':bid.auction.seller.ethereum_wallet_address,
            'seller_ethereum_wallet_private_key':bid.auction.seller.ethereum_wallet_private_key,
            'network':bid.auction.network, 
            'ethereum_token':bid.auction.seller.etherscan_token,
            'auction_contract_address':bid.auction.contract_address, 
        }
        #
        contractutils = ContractUtils()
        bc_setup = contractutils.set_up_blockchain(config)
        print(bc_setup)
        #
        print(bid.buyer.ethereum_wallet_address)
        transfer_tx_hash, transfer_tx_id = contractutils.transfer(
            bid.buyer.ethereum_wallet_address, 
            bid.buyer.ethereum_wallet_private_key, 
            bid.auction.seller.ethereum_wallet_address,
            bid.value, 
            bc_setup
        )
        for collection in bid.auction.collections.all():
            print(collection)
            for asset in collection.assets.all():
                print(asset)
                wallet_address = bid.buyer.ethereum_wallet_address
                mint_tx_hash, mint_tx_id = contractutils.web3_mint(
                    wallet_address,
                    asset.token_id,
                    bc_setup,
                )

                bid.status = "sold"
                bid.auction.status="sold"
                bid.auction.save()
                bid.save()

                new_purchase = Purchase()
                new_purchase.bid = bid
                new_purchase.mint_tx_hash = mint_tx_hash
                new_purchase.mint_tx_token = mint_tx_id
                #new_purchase.transfer_tx_hash = transfer_tx_hash
                #new_purchase.transfer_tx_token = transfer_tx_id
                new_purchase.save()
        #
    except Exception as err:
        #
        print("Purchase of NFT failed: {}".format(err))
    #
    return redirect(bid.auction)


@login_required
def bid_reject(request, bid_id):
    #
    bid = Bid.objects.get(id=bid_id)
    try:
        #
        bid.delete()
        #
    except Exception as err:
        #
        print("Failed to delete Bid: {}".format(err))
    #
    return redirect(auction)

