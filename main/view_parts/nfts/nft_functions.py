# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

#
from ...utils.ipfs import IPFSUtils

#
from ...forms import BidForm, NftForm
from ...models import Nft

#
from ..utils.pagination import *


def get_context_data(self, *args, **kwargs):
    #
    stuff = get_object_or_404(Nft, id=self.kwargs["pk"])
    total_likes = stuff.total_likes()
    context["total_likes"] = total_likes
    #
    return context


def likeview(request, pk):
    #
    nft = get_object_or_404(Nft, pk=pk)
    nft.likes.add(request.user)
    #
    return HttpResponseRedirect(reverse("nft_detail", args=[str(pk)]))


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


@login_required
def nft_detail(request, nft_uuid):
    #
    nft = Nft.objects.get(uuid=nft_uuid)
    bid_form = BidForm(request)
    #
    return render(
        request, "nfts/detail.html", {"nft": nft, "bid_form": bid_form}
    )


@login_required
def nfts_own(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user)
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list_image.html", context)


@login_required
def nfts_own_2d(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="2d")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list_image.html", context)


@login_required
def nfts_own_3d(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="3d")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list_image.html", context)


@login_required
def nfts_own_music(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="music")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list_music.html", context)


@login_required
def nfts_own_video(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="video")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list_video.html", context)


@login_required
def nfts_own_doc(request):
    #
    nfts_list = Nft.objects.filter(creator=request.user, nft_type="doc")
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/list_doc.html", context)