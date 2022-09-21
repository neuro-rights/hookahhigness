import boto3
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
from ...forms import BidForm, NftForm
from ...models import Asset, Auction, Nft

#
from ..utils.pagination import *



def search_result(request):
    #
    if request.method == "GET":
        searched = request.GET["searched"]
        search_result = Nft.objects.filter(nft_name__contains=searched)
        #
        context = {"searched": searched, "search_result": search_result}
        return render(request, "nfts/search.html", context)
    else:
        return render(request, "nfts/search.html")


def get_context_data(self, *args, **kwargs):
    #
    stuff = get_object_or_404(Nft, id=self.kwargs["pk"])
    total_likes = stuff.total_likes()
    context["total_likes"] = total_likes
    #
    return context


def like_nft(request, nft_uuid):
    """
    nft = get_object_or_404(Nft, uuid=nft_uuid)
    nft.likes.add(request.user)
    #
    return HttpResponseRedirect(reverse("nft_detail", args=[str(uuid)]))
    """
    pass


@login_required
def nft_detail(request, nft_uuid):
    #
    nft = Nft.objects.get(uuid=nft_uuid)
    #
    return render(
        request, "nfts/detail.html", {"nft": nft}
    )


@login_required
def nfts_own(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user)
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list.html", context)


@login_required
def nfts_own_2d(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="2d")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list.html", context)


@login_required
def nfts_own_3d(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="3d")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list.html", context)


@login_required
def nfts_own_music(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="music")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list.html", context)


@login_required
def nfts_own_video(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="video")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list.html", context)


@login_required
def nfts_own_doc(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="doc")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list.html", context)


def nft_add_auction(request, nft_uuid):
    nft = get_object_or_404(Nft, uuid=nft_uuid)
    #
    asset = Asset.objects.create(asset_type=nft.nft_type, seller=nft.creator, name=nft.name, description=nft.description)
    asset.nfts.add(nft)
    auction = Auction.objects.create(seller=nft.creator, description=nft.description, bid_start_value=0)
    auction.assets.add(asset)
    return HttpResponseRedirect(reverse("auction_detail", args=[str(auction.uuid)]))


@login_required
def nft_add_file(nft_uuid):
    pass


@login_required
def nft_add_file_to_s3(request, nft_uuid):
    """ """

    nft_file = request.FILES.get('photo-file', None)

    S3_BASE_URL = 'https://s3.'+request.user.aws_s3_region+'.amazonaws.com/'
    BUCKET = request.user.aws_s3_bucket

    # photo-file will be the "name" attribute on the <input type="file">
    if nft_file:

        s3 = boto3.client(
            "s3",
            aws_access_key_id=request.user.aws_access_key_id_value,
            aws_secret_access_key=request.user.aws_secret_access_key_value,
        )
        # need a unique "key" for S3 / needs image file extension too
        key = uuid.uuid4().hex[:6] + nft_file.name[nft_file.name.rfind('.'):]
        # just in case something goes wrong
        try:
            s3.upload_fileobj(nft_file, request.user.aws_s3_bucket, key, ExtraArgs={'ACL': 'public-read'})
            # build the full url string
            url = f"{S3_BASE_URL}/{BUCKET}/{key}"
            nft = Nft.objects.get(uuid=nft_uuid)
            nft.uri_preview = url
            nft.save()
            return render(
                request, "nfts/detail.html", {"nft": nft}
            )
        except:
            print("An error occurred uploading file to S3")


@login_required
def nft_ipfs_upload_asset(asset_file):
    if asset_file:
        try:
            ipfsutils = IPFSUtils()
            url = ipfsutils.ipfs_upload(asset_file)
            nft = Nft.objects.get(uuid=nft_uuid)
            nft.preview_image = url
            nft.asset_uri = url
            # TODO
            # nft.metadata_uri = ""
            nft.save()

        except:
            print("An error occurred uploading file to IPFS")
        #
        return redirect("nft_detail", uuid=nft_uuid)

