import boto3
import time
import uuid

# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core import serializers
#
from ...utils.ipfs import IPFSUtils

#
from ...forms import BidForm, AssetForm
from ...models import Collection, Auction, Asset

#
from ..utils.pagination import *


def search_result(request):
    #
    if request.method == "GET":
        searched = request.GET["searched"]
        search_result = Asset.objects.filter(asset_name__contains=searched)
        #
        context = {"searched": searched, "search_result": search_result}
        return render(request, "assets/search.html", context)
    else:
        return render(request, "assets/search.html")


def get_context_data(self, *args, **kwargs):
    #
    stuff = get_object_or_404(Asset, id=self.kwargs["pk"])
    total_likes = stuff.total_likes()
    context["total_likes"] = total_likes
    #
    return context


def like_asset(request, asset_uuid):
    """
    asset = get_object_or_404(Asset, uuid=asset_uuid)
    asset.likes.add(request.user)
    #
    return HttpResponseRedirect(reverse("asset_detail", args=[str(uuid)]))
    """
    pass


@login_required
def asset_detail(request, asset_uuid):
    #
    asset = Asset.objects.get(uuid=asset_uuid)
    #
    return render(
        request, "assets/detail.html", {"asset": asset}
    )


@login_required
def assets_own(request):
    #
    assets_list = Asset.objects.filter(creator=request.user)
    #
    context = {"page_obj": get_page_obj(request, assets_list, 25)}
    return render(request, "assets/list.html", context)


@login_required
def assets_own_2d(request):
    #
    assets_list = Asset.objects.filter(creator=request.user, asset_type="2d")
    #
    context = {"page_obj": get_page_obj(request, assets_list, 25)}
    return render(request, "assets/list.html", context)


@login_required
def assets_own_3d(request):
    #
    assets_list = Asset.objects.filter(creator=request.user, asset_type="3d")
    #
    context = {"page_obj": get_page_obj(request, assets_list, 25)}
    return render(request, "assets/list.html", context)


@login_required
def assets_own_music(request):
    #
    assets_list = Asset.objects.filter(creator=request.user, asset_type="music")
    #
    context = {"page_obj": get_page_obj(request, assets_list, 25)}
    return render(request, "assets/list.html", context)


@login_required
def assets_own_video(request):
    #
    assets_list = Asset.objects.filter(creator=request.user, asset_type="video")
    #
    context = {"page_obj": get_page_obj(request, assets_list, 25)}
    return render(request, "assets/list.html", context)


@login_required
def assets_own_doc(request):
    #
    assets_list = Asset.objects.filter(creator=request.user, asset_type="doc")
    #
    context = {"page_obj": get_page_obj(request, assets_list, 25)}
    return render(request, "assets/list.html", context)


def asset_add_auction(request, asset_uuid):
    asset = get_object_or_404(Asset, uuid=asset_uuid)
    #
    collection = Collection.objects.create(
            collection_type=asset.asset_type, 
            seller=asset.creator, 
            name=asset.name, 
            description=asset.description, 
            uri_preview=asset.uri_preview
    )
    
    collection.assets.add(asset)
    auction = Auction.objects.create(
            seller=asset.creator, 
            description=asset.description, 
            bid_start_value=0, 
            uri_preview=asset.uri_preview
    )
    auction.collections.add(collection)
    return HttpResponseRedirect(reverse("auction_detail", args=[str(auction.uuid)]))


@login_required
def asset_add_file_to_s3(request, asset_uuid):
    """ """

    asset_file = request.FILES.get('photo-file', None)
    asset = Asset.objects.get(uuid=asset_uuid)

    S3_BASE_URL = 'https://s3.'+request.user.aws_s3_region+'.amazonaws.com'
    BUCKET = request.user.aws_s3_bucket

    # photo-file will be the "name" attribute on the <input type="file">
    if asset_file:

        s3 = boto3.client(
            "s3",
            aws_access_key_id=request.user.aws_access_key_id_value,
            aws_secret_access_key=request.user.aws_secret_access_key_value,
        )
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + asset_file.name[asset_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            s3.upload_fileobj(asset_file, request.user.aws_s3_bucket, key, ExtraArgs={'ACL': 'public-read'})
            # build the full url string
            url = f"{S3_BASE_URL}/{BUCKET}/{key}"
            asset.uri_preview = url
            asset.save()
        except:
            print("An error occurred uploading file to S3")
        
        return redirect(asset)


@login_required
def asset_ipfs_upload_file(request, asset_uuid):
    """ """
    asset_file = request.FILES.get('photo-file', None)
    asset = Asset.objects.get(uuid=asset_uuid)
    if asset_file:
        try:
            ipfsutils = IPFSUtils()
            url = ipfsutils.infura_ipfs_upload(asset_file)
            asset.uri_preview = url
            asset.uri_asset = url
            # TODO
            # asset.metadata_uri = ""
            asset.save()

        except:
            print("An error occurred uploading file to IPFS")
        #
        return redirect(asset)

