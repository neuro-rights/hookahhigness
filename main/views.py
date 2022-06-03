from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from .models import NFT, NFTCollection, Photo, Sell, Bid, Profile
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.core import serializers
from django.core.paginator import Paginator

# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from .forms import BidForm, SellForm, FileFieldForm, NFTCollectionForm, ProfileForm

import pprint
import uuid

import requests
from requests import HTTPError
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
def add_nfts(request, collection_id):
    #
    files = request.FILES.getlist("file_field")
    collection = NFTCollection.objects.get(id=collection_id)
    counter = 0
    ipfsutils = IPFSUtils()
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
    paginator = Paginator(collection_nfts, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    #
    return render(
        request,
        "collections/detail.html",
        {"collection": collection, "collection_nfts": collection_nfts, "page_obj": page_obj},
    )


@login_required
def collection_index(request):
    #
    collections_list = NFTCollection.objects.all()
    paginator = Paginator(collections_list, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "main/nftcollection_list.html", {"collections_list": collections_list, "page_obj": page_obj})


class NFTCollectionCreate(LoginRequiredMixin, CreateView):
    """ """

    form_class = NFTCollectionForm
    model = NFTCollection
    fields = ["name", "description", "blockchain", "metadata_file", "metadata_dir_url"]
    template_name = "main/nftcollection_form.html"
    #

    def get(self, request, *args, **kwargs):
        #
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        #
        form = self.form_class(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        #
        collection = form.save(commit=False)
        collection.creator = request.user
        collection.save()
        print(collection.__dict__)
        #
        # https://gateway.pinata.cloud/ipfs/QmX232ULoePr7nRBndq5Vj5kSmjAjuhdv5Gks2Uisnc3qc/_metadata.json
        #
        counter = 0
        print("Loading Metadata: ")
        metadata = json.loads(collection.metadata_file.open("r").read())
        print("Loaded Metadata: {}".format(metadata))
        for f in metadata:
            nft_image_uri = f["image"]
            nft_meta_filename = "{}.json".format(Path(nft_image_uri).stem)
            nft_meta_uri = os.path.join(collection.metadata_dir_url, nft_meta_filename)
            #
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
                print("Adding new NFT to collection: {}".format(nft.id))
            except Exception as e:
                print(e)
            try:
                photo = Photo(url=nft_image_uri, nft_id=nft.id)
                photo.save()
            except Exception as e:
                print(e)
            #
            counter += 1
        #
        # return render(request, "collections/detail.html", {"collection_id": collection.id})
        return redirect("/collections/all")


class NFTCollectionEdit(LoginRequiredMixin, UpdateView):
    """ """

    form_class = NFTCollectionForm
    model = NFTCollection
    fields = ["name", "description", "blockchain", "metadata_file", "metadata_dir_url"]
    template_name = "main/nftcollection_form.html"
    #

    def get(self, request, *args, **kwargs):
        #
        form = self.form_class(self.object.id)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        #
        form = self.form_class(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        #
        collection = form.save()
        # collection.nfts.delete()
        print(collection.__dict__)
        #
        counter = 0
        print("Loading Metadata: ")
        metadata = json.loads(collection.metadata_file.open("r").read())
        print("Loaded Metadata: ")
        for f in metadata:
            nft_image_uri = f["image"]
            nft_meta_filename = "{}.json".format(Path(nft_image_uri).stem)
            nft_meta_uri = os.path.join(collection.metadata_dir_url, nft_meta_filename)
            #
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
                print("Adding new NFT to collection: {}".format(nft.id))
            except Exception as e:
                print(e)
            try:
                photo = Photo(url=nft_image_uri, nft_id=nft.id)
                photo.save()
            except Exception as e:
                print(e)
            #
            counter += 1
        #
        return redirect("/collections/all")


class NFTCollectionDelete(LoginRequiredMixin, DeleteView):
    """ """

    model = NFTCollection
    success_url = "/collections/all"


class NFTCollectionList(ListView):
    """ """

    paginate_by = 10
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

    paginate_by = 10
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
    paginator = Paginator(nfts_list, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    #
    return render(request, "nfts/own.html", {"nfts_list": nfts_list, "page_obj": page_obj})


@login_required
def collection_own(request):
    #
    collections_list = NFTCollection.objects.filter(creator=request.user)
    paginator = Paginator(collections_list, 10)  # Show 10 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    #
    return render(request, "collections/own.html", {"collections_list": collections_list, "page_obj": page_obj})


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
    collections_list = NFTCollection.objects.all()
    nfts_list = NFT.objects.all()
    return render(request, "home.html", {"collections_list": collections_list, "nfts_list": nfts_list})


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
