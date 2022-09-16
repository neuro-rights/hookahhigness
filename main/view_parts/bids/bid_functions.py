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
from ...forms import PurchaseForm
from ...models import User, Bid, Purchase


@login_required
def bid_accept(request, bid_uuid):
    #
    try:
        #
        contract_address = os.environ["CONTRACT_ADDRESS"]
        contract_abi = os.environ["CONTRACT_ABI"]
        #
        bid = Bid.objects.get(uuid=bid_uuid)
        auction_assets = bid.auction.get_assets()
        auction_assets_nfts = [a.nfts.all() for a in auction_assets]
        user_wallet = (
            Profile.object.select_related("user")
            .get(user=bid.bidder)
            .wallet_address
        )
        #
        nftutils = NFTUtils()
        bc_setup = nftutils.set_up_blockchain(
            contract=contract_address, abi_path=contract_abi
        )
        tx_hash, tx_token = nftutils.web3_mint(
            userAddress=user_wallet,
            tokenURI=nft_metadata_uri,
            eth_json=bc_setup,
        )
        #
        new_purchase = Purchase(commit=False)
        new_purchase.bid_id = bid_id
        new_purchase.tx_hash = tx_hash
        new_purchase.tx_token = tx_token
        new_purchase.save()
        #
    except Exception as err:
        #
        print("Purchase of NFT failed: {}".format(err))
        return redirect("nft_detail", nft_id=bid.nft_id)
    #
    return redirect("nft_detail", nft_id=bid.nft_id)


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
