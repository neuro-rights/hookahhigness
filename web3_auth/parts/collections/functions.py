import boto3
import json
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
from ...forms import BidForm, PurchaseForm
from ...models import User, Collection, Bid, Auction, Purchase, Asset
#
from ...utils.ipfs import IPFSUtils
#
from ..utils.pagination import *


@login_required
def collection_detail(request, collection_uuid):
    #
    collection = Collection.objects.get(uuid=collection_uuid)

    return render(
        request, "collections/detail.html", {"collection": collection}
    )


@login_required
def collections_list(request):
    #
    collections_list = Collection.objects.order_by("-id").all()
    #
    context = {"page_obj": get_page_obj(request, collections_list, 25)}
    return render(request, "collections/list.html", context)


@login_required
def collections_own(request):
    #
    collections_own = Collection.objects.filter(seller=request.user)
    #
    context = {"page_obj": get_page_obj(request, collections_own, 25)}
    return render(request, "collections/list.html", context)


@login_required
def collection_add_raffle(request, auction_uuid):
    return redirect(collection)


@login_required
def collection_add_auction(request, collection_uuid):
    #
    collection = Collection.objects.get(uuid=collection_uuid)
    auction = Auction(
            seller=collection.seller,
            description=collection.description,
            bid_start_value=0,
            uri_preview=collection.uri_preview
    )
    form = BidForm()
    #
    auction.save()
    auction.collections.add(collection)
    return redirect(auction)


@login_required
def collection_add_metadata(request, auction_id):
    #
    collection = Collection.objects.filter(creator=request.user)
    return redirect(collection)


@login_required
def collection_ipfs_upload_files(request, collection_uuid):
    #
    files = request.FILES.getlist("asset-files")
    collection = Collection.objects.get(uuid=collection_uuid)
    counter = 0
    ipfsutils = IPFSUtils()
    #
    for f in files:
        url = ipfsutils.infura_ipfs_upload(f)
        # TODO - generate metadata
        try:
            asset = Asset(
                name="{}_{}".format(collection.name, counter),
                description=collection.description,
                creator=request.user,
                uri_preview=url,
                #uri_metadata="",
                uri_asset=url,
                asset_type=collection.collection_type
            )
            asset.save()
            collection.uri_preview = asset.uri_preview
            #collection.uri_metadata
            collection.assets.add(asset)
            collection.save()
            print("asset uri"+asset.uri_preview)
            print("collection uri"+collection.uri_preview)
        except Exception as e:
            print(e)
        counter += 1

    return redirect(collection)


@login_required
def collection_add_files_to_s3(request, collection_uuid):
    """ """

    asset_files = request.FILES.getlist("files-field")
    collection = Collection.objects.get(uuid=collection_uuid)

    S3_BASE_URL = 'https://s3.'+request.user.aws_s3_region+'.amazonaws.com/'
    BUCKET = request.user.aws_s3_bucket

    # photo-file will be the "name" attribute on the <input type="file">
    counter = 0
    for asset_file in asset_files:
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
                print(url)
                # create asset
                asset = Asset()
                asset.name="{}_{}".format(collection.name, counter)
                asset.description=collection.description
                asset.creator=request.user
                asset.uri_preview=url
                asset.uri_metadata=""
                asset.uri_collection=url
                asset.uri_preview = url
                asset.save()
                # add asset to collection
                collection.assets.add(asset)
                counter += 1

            except Exception as e:
                print("An error occurred uploading file to S3 - {}".format(e))

    return redirect(collection)

def collection_asset_files(request, collection_uuid):
    collection = Collection.objects.get(uuid=collection_uuid)
    f = request.FILES.get('asset-files', None)

def collection_metadata_file(request, collection_uuid):
    """
    """
    counter = 0
    collection = Collection.objects.get(uuid=collection_uuid)
    f = request.FILES.get('json-file', None)
    metadata = json.load(f)
    print(metadata)
    for asset_metadata in metadata:
        try:
            url = asset_metadata["image"]
            print(url)
            collection.uri_preview = url
            collection.uri_metadata = url
            asset = Asset(
                name="{}_{}".format(collection.name, counter),
                description=collection.description,
                creator=request.user,
                asset_type=collection.collection_type,
                uri_metadata=url,
                uri_preview=url,
            )
            asset.save()
            collection.assets.add(asset)
            collection.save()
            print("Adding new NFT to collection: {}".format(asset.uuid))
            counter += 1
        except Exception as e:
            print(e)
    
    return redirect('/')



def like_collection(request, collection_uuid):
    """
    asset = get_object_or_404(Asset, uuid=asset_uuid)
    asset.likes.add(request.user)
    #
    return HttpResponseRedirect(reverse("asset_detail", args=[str(uuid)]))
    """
    pass

