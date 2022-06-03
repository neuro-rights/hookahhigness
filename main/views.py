from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from .models import NFT, NFTCollection, Photo, Sell, Bid, Profile
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse

# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from .forms import BidForm, SellForm, FileFieldForm, NFTCollectionForm, ProfileForm

import pprint
import uuid

import requests
import json
import os
from pathlib import Path
import sys

import logging

from .utils.nft import NFTUtils
from .utils.ipfs import IPFSUtils
from .utils.contract import ContractUtils


@login_required
def add_photo(request, nft_id):
    #
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


@login_required
def add_collection_metadata(request, collection_id):
    #
    if not request.collection_metadata_url:
        print(json.dumps(request, indent=4))
        exit(1)
    #
    metadata = json.loads(request.collection_metadata_url)
    collection = NFTCollection.objects.get(id=collection_id)
    counter = 0

    # https://gateway.pinata.cloud/ipfs/QmX232ULoePr7nRBndq5Vj5kSmjAjuhdv5Gks2Uisnc3qc/_metadata.json
    #
    for f in metadata:
        nft_image_uri = f.image
        nft_meta_filename = "{}.json".format(Path(f.collection_metadata).stem)
        nft_meta_dir = Path(request.collection_metadata_url).parents[0]
        nft_meta_uri = os.path.join(nft_meta_dir, nft_meta_filename)

        try:
            nft = NFT(
                nft_name="{}_{}".format(collection.name, counter),
                description=collection.description,
                blockchain=collection.blockchain,
                creator_id=request.user.id,
                metadata_uri=nft_meta_uri,
            )
            nft.save()
            collection.nfts.add(nft)
            print(nft.id)
        except Exception as e:
            print(e)
        try:
            photo = Photo(url=nft_image_uri, nft_id=nft.id)
            photo.save()
        except Exception as e:
            print(e)
        counter += 1
    #
    return render(request, "collections/detail.html", {"collection": collection})


@login_required
def add_nfts(request, collection_id):
    #
    files = request.FILES.getlist("file_field")
    collection = NFTCollection.objects.get(id=collection_id)
    counter = 0
    ipfsutils = IPFSUtils()

    # https://gateway.pinata.cloud/ipfs/QmX232ULoePr7nRBndq5Vj5kSmjAjuhdv5Gks2Uisnc3qc/_metadata.json
    # https://gateway.pinata.cloud/ipfs/QmbL4rkkbW5AWG2RdM2PxA9PKnS78GoT7G8CuVQ3g2eg4H/
    #
    for f in files:
        url = ipfsutils.ipfs_upload(f)
        try:
            nft = NFT(
                nft_name="{}_{}".format(collection.name, counter),
                description=collection.description,
                blockchain=collection.blockchain,
                creator_id=request.user.id,
            )
            nft.save()
            collection.nfts.add(nft)
            print(nft.id)
        except Exception as e:
            print(e)
        try:
            photo = Photo(url=url, nft_id=nft.id)
            photo.save()
        except Exception as e:
            print(e)
        counter += 1
    #
    return render(request, "collections/detail.html", {"collection": collection})


@login_required
def collection_detail(request, collection_id):
    #
    collection = NFTCollection.objects.get(id=collection_id)
    collection_nfts = collection.nfts.all()
    #
    return render(request, "collections/detail.html", {"collection": collection, "collection_nfts": collection_nfts})


@login_required
def collection_index(request):
    #
    collections = NFTCollection.objects.all()
    #
    return render(request, "main/nftcollection_list.html", {"collections": collections})


class NFTCollectionCreate(LoginRequiredMixin, CreateView):
    """ """

    model = NFTCollection
    fields = ["name", "description", "blockchain"]
    template_name = "main/nftcollection_form.html"
    #
    def get_success_url(self):
        return reverse("collection_detail", kwargs={"collection_id": self.object.id})

    #
    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class NFTCollectionEdit(LoginRequiredMixin, UpdateView):
    """ """

    model = NFTCollection
    fields = ["name", "description", "blockchain"]
    template_name = "main/nftcollection_form.html"
    #
    def get_success_url(self):
        return reverse("collection_detail", kwargs={"collection_id": self.object.id})

    #
    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class NFTCollectionDelete(LoginRequiredMixin, DeleteView):
    """ """

    model = NFTCollection
    success_url = "/collections/all"


class NFTCollectionList(ListView):
    """ """

    model = NFTCollection


class NFTCreate(LoginRequiredMixin, CreateView):
    """ """

    model = NFT
    fields = ["nft_name", "description"]
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
    fields = ["nft_name", "description"]
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
    success_url = "/nfts/"


class NFTList(ListView):
    """ """

    model = NFT


@login_required
def nft_detail(request, nft_id):
    #
    nft = NFT.objects.get(id=nft_id)
    bid_form = BidForm()
    #
    return render(request, "nfts/detail.html", {"nft": nft, "bid_form": bid_form})


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
def nft_own(request):
    #
    nfts_list = NFT.objects.filter(creator=request.user)
    #
    return render(request, "nfts/own.html", {"nfts_list": nfts_list})


@login_required
def collection_own(request):
    #
    collection_list = NFTCollection.objects.filter(creator=request.user)
    #
    return render(request, "collections/own.html", {"collection_list": collection_list})


def signup(request):
    #
    error_message = ""
    #
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/accounts/settings")
        else:
            error_message = "Invalid sign up - try again"
    #
    form = UserCreationForm()
    context = {"form": form, "error_message": error_message}
    #
    return render(request, "registration/signup.html", context)


@login_required
def settings(request):
    #
    error_message = ""
    #
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()
            context = {"form": form, "error_message": error_message}
            return render(request, "registration/settings.html", context)
        else:
            error_message = "Invalid account - try again"
    #
    form = ProfileForm()
    context = {"form": form, "error_message": error_message}
    #
    return render(request, "registration/settings.html", context)


def home(request):
    #
    collections = NFTCollection.objects.all()
    nfts_list = NFT.objects.all()
    return render(request, "home.html", {"collections": collections, "nfts_list": nfts_list})


def search_result(request):
    #
    if request.method == "GET":
        searched = request.GET["searched"]
        search_result = NFT.objects.filter(nft_name__contains=searched)
        return render(request, "main/nft_search_result.html", {"searched": searched, "search_result": search_result})
    else:
        return render(request, "main/nft_search_result.html")


@login_required
def sell(request, nft_id):
    #
    form = SellForm(request.POST)
    if form.is_valid():
        new_sell = form.save(commit=False)
        new_sell.nft_id = nft_id
        new_sell.save()
        return redirect("nft_detail", nft_id=nft_id)
    #
    return render(request, "main/sell_form.html", {"nft": nft_id, "form": form})


@login_required
def accept_bid(request, bid_id):
    #
    try:
        #
        contract_address = os.environ["CONTRACT_ADDRESS"]
        contract_abi = os.environ["CONTRACT_ABI"]
        #
        bid = Bid.objects.get(id=bid_id)
        nft_metadata_uri = bid.nft.metadata_uri
        user_wallet = Profile.object.select_related("user").get(user=bid.bidder).wallet_address
        #
        nftutils = NFTUtils()
        bc_setup = nftutils.set_up_blockchain(contract=contract_address, abi_path=contract_abi)
        tx_hash, tx_token_id = nftutils.web3_mint(userAddress=user_wallet, tokenURI=nft_metadata_uri, eth_json=bc_setup)
        #
        new_purchase = Purchase(commit=False)
        new_purchase.bid_id = bid_id
        new_purchase.tx_hash = tx_hash
        new_purchase.tx_token_id = tx_token_id
        new_purchase.save()
        #
    except Exception as err:
        #
        print("Purchase of NFT failed: {}".format(err))
        return redirect("nft_detail", nft_id=bid.nft_id)
    #
    return redirect("nft_detail", nft_id=bid.nft_id)


@login_required
def reject_bid(request, bid_id):
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
def add_bid(request, nft_id):
    #
    form = BidForm(request.POST)
    sale = Sell.objects.select_related("nft").get(id=nft_id)
    #
    if not form.is_valid():
        return redirect("nft_detail", nft_id=nft_id)
    #
    new_bid = form.save(commit=False)
    if new_bid.bid_price <= sale.min_bid_price:
        return redirect("nft_detail", nft_id=nft_id)
    #
    sale.min_bid_price = new_bid.bid_price
    sale.save()
    #
    new_bid.nft_id = nft_id
    new_bid.bidder_id = request.user.id
    new_bid.save()
    #
    return redirect("nft_detail", nft_id=nft_id)


def all_for_sale(request):
    #
    nfts_list = NFT.objects.all()
    return render(request, "nfts/for_sale.html", {"nfts_list": nfts_list})
