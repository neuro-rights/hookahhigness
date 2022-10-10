# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape


#
from ...forms import (
    CollectionForm,
    CollectionFromFilesForm,
    CollectionFromAssetsForm,
    CollectionFromMetadataURLForm,
)
from ...models import Asset, Collection
from ...utils.ipfs import IPFSUtils

#
from ..utils.pagination import *
from ..utils.form_kwargs import PassArgumentsToForm


import boto3

S3_BASE_URL = "https://s3.us-east-1.amazonaws.com/"
BUCKET = "nftmarketgallery"


class CollectionFromFilesCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = CollectionFromFilesForm
    model = Collection
    template_name = "collections/form.html"
    #
    def get_success_url(self):
        return reverse("collection_detail", kwargs={"collection_uuid": self.object.uuid})
    #
    def post(self, request, *args, **kwargs):
        #
        form = self.form_class(
            request, request.POST, request.FILES
        )
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        #
        collection = form.save(commit=False)
        collection.creator = request.user
        collection.save()
        print(collection.__dict__)
        #
        # https://gateway.pinata.cloud/ipfs/QmX232ULoePr7nRBndq5Vj5kSmjAjuhdv5Gks2Uisnc3qc/_metadata.json
        ipfsutils = IPFSUtils()
        counter = 0
        for collection_file in request.FILES:
            # upload file
            asset_collection_uri = ipfsutils.pinContentToIPFS(collection_file)
            # Create metadata
            asset_metadata = {
                "name": "{}_{}".format(collection.name, counter),
                "description": collection.description,
                "collection": asset_collection_uri,
                "edition": counter,
            }
            # upload metadata
            asset_metadata_uri = ipfsutils.pinJSONToIPFS(asset_metadata)
            #
            try:
                asset = Asset(
                    name="{}_{}".format(collection.name, counter),
                    description=collection.description,
                    creator=request.user,
                    asset_type=collection.collection_type,
                    uri_metadata=asset_metadata_uri,
                    uri_collection=asset_collection_uri,
                    uri_preview=asset_collection_uri,
                )
                asset.save()
                collection.assets.add(asset)
                print("Adding new NFT to collection: {}".format(asset.id))
            except Exception as e:
                print(e)
            #
            counter += 1
        #
        return redirect("/collections/own/")


class CollectionFromAssetsCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = CollectionFromAssetsForm
    model = Collection
    template_name = "collections/form.html"
    #
    def get_success_url(self):
        return reverse("collection_detail", kwargs={"collection_uuid": self.object.uuid})


class CollectionFromMetadataURLCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = CollectionFromMetadataURLForm
    model = Collection
    template_name = "collections/form.html"
    #
    def get_success_url(self):
        return reverse("collection_detail", kwargs={"collection_uuid": self.object.uuid})
    #
    def post(self, request, *args, **kwargs):
        #
        form = self.form_class(
            request, request.POST, request.FILES
        )
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
        collection_metadata = requests.get(collection.uri_metadata).json()
        print("Loaded Metadata: {}".format(metadata))
        asset_metadata_dir = Path(collection.uri_metadata).resolve().parent
        for asset_metadata in collection_metadata:
            asset_collection_uri = asset_metadata["image"]
            asset_collection_filename = "{}.json".format(
                Path(collection.uri_metadata).resolve().stem
            )
            asset_metadata_uri = os.path.join(
                asset_metadata_dir, asset_collection_filename
            )
            #
            try:
                asset = Asset(
                    name="{}_{}".format(collection.name, counter),
                    description=collection.description,
                    creator=request.user,
                    asset_type=collection.collection_type,
                    uri_metadata=asset_metadata_uri,
                    uri_collection=asset_collection_uri,
                    uri_preview=asset_collection_uri,
                )
                asset.save()
                collection.assets.add(asset)
                print("Adding new NFT to collection: {}".format(asset.uuid))
            except Exception as e:
                print(e)
            #
            counter += 1
        #
        return redirect("/collections/own/")


class CollectionCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = CollectionForm
    model = Collection
    template_name = "collections/form.html"
    #
    def get_success_url(self):
        return reverse("collection_detail", kwargs={"collection_uuid": self.object.uuid})


class CollectionEdit(PassArgumentsToForm, UpdateView):
    """ """

    form_class = CollectionForm
    model = Collection
    template_name = "collections/form.html"
    #
    def get_object(self, queryset=None):
        return Collection.objects.get(uuid=self.kwargs.get("collection_uuid"))
    #
    def get_success_url(self):
        return reverse("collection_detail", kwargs={"collection_uuid": self.object.uuid})
    #
    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)


class CollectionDelete(LoginRequiredMixin, DeleteView):
    """ """

    model = Collection
    success_url = "/collections/own/"
    template_name = "collections/delete.html"
    #
    def get_object(self, queryset=None):
        return Collection.objects.get(uuid=self.kwargs.get("collection_uuid"))


class CollectionList(PassArgumentsToForm, ListView):
    """ """

    paginate_by = 25
    model = Collection
    fields = [
        "name",
        "description",
        "seller",
        "collection_type",
        "status"
    ]
    template_name = "collections/list.html"

    def get_querset(self):
        return Collection.objects.filter(seller=self.request.user)



class CollectionListJson(BaseDatatableView):
    model = Collection
    # define the columns that will be returned
    columns = ['uuid', 'collection_type', 'seller', 'assets', 'name', 'status']
    order_columns = ['uuid', 'collection_type', 'seller', 'assets', 'name', 'status']

    def get_initial_queryset(self):
        return Collection.objects.filter(seller=self.request.user)


class CollectionDetailView(PassArgumentsToForm, DetailView):
    """ """

    model = Collection
    form_class = CollectionForm
    template_name = "collections/detail.html"

    def get_object(self, queryset=None):
        return Collection.objects.get(uuid=self.kwargs.get("collection_uuid"))
