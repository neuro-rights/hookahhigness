# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.urls import reverse

#
from ..forms import NFTCollectionForm
from ..models import NFT, NFTCollection, Photo
from ..utils.ipfs import IPFSUtils
from .pagination import *

#
import pprint
import uuid
import requests
from requests import HTTPError
import json
import os
from pathlib import Path
import sys
import logging


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
        return redirect("/collections/")


class NFTCollectionEdit(LoginRequiredMixin, UpdateView):
    """ """

    model = NFTCollection
    fields = ["name", "description", "blockchain", "metadata_file", "metadata_dir_url"]
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
    success_url = "/collections/"

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.nfts.all().delete()
        return super(NFTCollectionDelete, self).delete(*args, **kwargs)


class NFTCollectionList(ListView):
    """ """

    paginate_by = 25
    model = NFTCollection


@login_required
def collection_detail(request, collection_id):
    #
    collection = NFTCollection.objects.get(id=collection_id)
    collection_nfts = collection.nfts.order_by("likes").all()
    #
    context = {
        "collection": collection,
        "page_obj": get_page_obj(request, collection_nfts, 25),
    }
    return render(request, "collections/detail.html", context)


@login_required
def collection_index(request):
    #
    collections_list = NFTCollection.objects.order_by("-id").all()
    #
    context = {"page_obj": get_page_obj(request, collections_list, 25)}
    return render(request, "main/nftcollection_list.html", context)


@login_required
def collection_own(request):
    #
    collections_list = NFTCollection.objects.filter(creator=request.user)
    #
    context = {"page_obj": get_page_obj(request, collections_list, 25)}
    return render(request, "collections/own.html", context)


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
    context = {"collection": collection}
    return render(request, "collections/detail.html", context)
