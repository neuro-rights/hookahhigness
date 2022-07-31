# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

#
from ...forms import PurchaseForm
from ...models import User, Asset, Bid, Purchase

#
from ..utils.pagination import *


@login_required
def asset_detail(request, asset_uuid):
    #
    asset = Asset.objects.get(uuid=asset_uuid)
    asset_nfts = asset.nfts.order_by("likes").all()
    #
    context = {
        "asset": asset,
        "page_obj": get_page_obj(request, asset_nfts, 25),
    }
    return render(request, "assets/detail.html", context)


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
def asset_add_raffle(request, auction_id):
    pass


@login_required
def asset_add_auction(request, auction_id):
    #
    asset = Asset.objects.filter(creator=request.user)
    #
    context = {"asset": asset}
    return render(request, "assets/list.html", context)


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
