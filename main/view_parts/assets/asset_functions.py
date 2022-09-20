# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core import serializers
#
from ...forms import BidForm, PurchaseForm
from ...models import User, Asset, Bid, Auction, Purchase

#
from ..utils.pagination import *


@login_required
def asset_detail(request, asset_uuid):
    #
    asset = Asset.objects.get(uuid=asset_uuid)
    bid_form = BidForm(request)

    return render(
        request, "assets/detail.html", {"asset": asset, "bid_form": bid_form}
    )


@login_required
def assets_list(request):
    #
    assets_list = Asset.objects.order_by("-id").all()
    #
    context = {"page_obj": get_page_obj(request, assets_list, 25)}
    return render(request, "assets/list.html", context)


@login_required
def assets_own(request):
    #
    assets_own = Asset.objects.filter(seller=request.user)
    #
    context = {"page_obj": get_page_obj(request, assets_own, 25)}
    return render(request, "assets/list.html", context)


@login_required
def asset_add_raffle(request, auction_uuid):
    pass


@login_required
def asset_add_auction(request, asset_uuid):
    #
    asset = Asset.objects.get(uuid=asset_uuid)
    auction = Auction(
            seller=asset.seller,
            description=asset.description,
            bid_start_value=0
    )
    form = BidForm()
    #
    auction.save()
    auction.assets.add(asset)
    context = {"auction": auction, "bid_form": form}
    return render(request, "auctions/detail.html", context)


@login_required
def asset_add_metadata(request, auction_id):
    #
    asset = Asset.objects.filter(creator=request.user)
    #
    context = {"asset": asset}
    return render(request, "assets/detail.html", context)


@login_required
def asset_add_nfts(request, asset_uuid):
    #
    files = request.FILES.getlist("file_field")
    asset = Asset.objects.get(uuid=asset_uuid)
    counter = 0
    ipfsutils = IPFSUtils()
    #
    for f in files:
        url = ipfsutils.ipfs_upload(f)
        # TODO generate metadata
        try:
            nft = Nft(
                nft_name="{}_{}".format(asset.name, counter),
                description=asset.description,
                creator=request.user,
                uri_preview=url,
                uri_metadata="",
                uri_asset=url,
            )
            nft.save()
            asset.nfts.add(nft)
            print(nft.id)
        except Exception as e:
            print(e)
        counter += 1

    context = {"asset": asset}
    return render(request, "assets/detail.html", context)

def like_asset(request, asset_uuid):
    """
    nft = get_object_or_404(Nft, uuid=nft_uuid)
    nft.likes.add(request.user)
    #
    return HttpResponseRedirect(reverse("nft_detail", args=[str(uuid)]))
    """
    pass

