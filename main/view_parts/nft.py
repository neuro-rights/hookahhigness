# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.urls import reverse

#
from ..forms import BidForm
from ..models import NFT, Photo
from ..utils.ipfs import IPFSUtils
from .pagination import *

#
import pprint
import uuid


class NFTCreate(LoginRequiredMixin, CreateView):
    """ """

    model = NFT
    fields = ["nft_name", "metadata_uri", "blockchain", "description"]
    #
    def get_success_url(self):
        return reverse("nft_detail", kwargs={"nft_id": self.object.id})

    #
    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class NFTEdit(LoginRequiredMixin, UpdateView):
    """ """

    model = NFT
    fields = ["nft_name", "metadata_uri", "blockchain", "description"]
    #
    def get_success_url(self):
        return reverse("nft_detail", kwargs={"nft_id": self.object.id})

    #
    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class NFTDelete(LoginRequiredMixin, DeleteView):
    """ """

    model = NFT
    success_url = "/nfts/own"


class NFTList(ListView):
    """ """

    paginate_by = 25
    model = NFT


@login_required
def nft_detail(request, nft_id):
    #
    nft = NFT.objects.get(id=nft_id)
    bid_form = BidForm()
    #
    return render(request, "nfts/detail.html", {"nft": nft, "bid_form": bid_form})


@login_required
def nft_own(request):
    #
    nfts_list = NFT.objects.filter(creator=request.user)
    #
    context = {"page_obj": get_page_obj(request, nfts_list, 25)}
    return render(request, "nfts/own.html", context)


def get_context_data(self, *args, **kwargs):
    #
    stuff = get_object_or_404(NFT, id=self.kwargs["pk"])
    total_likes = stuff.total_likes()
    context["total_likes"] = total_likes
    #
    return context


def likeview(request, pk):
    #
    nft = get_object_or_404(NFT, pk=pk)
    nft.likes.add(request.user)
    #
    return HttpResponseRedirect(reverse("nft_detail", args=[str(pk)]))


@login_required
def add_photo(request, nft_id):
    # photo-file will be the "name" attribute on the <input type="file">
    photo_file = request.FILES.get("photo-file", None)
    #
    if photo_file:
        try:
            ipfsutils = IPFSUtils()
            url = ipfsutils.ipfs_upload(photo_file)
            photo = Photo(url=url, nft_id=nft_id)
            photo.save()
        except:
            print("An error occurred uploading file to IPFS")
        #
        return redirect("nft_detail", nft_id=nft_id)
