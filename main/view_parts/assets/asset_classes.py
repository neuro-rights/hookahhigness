# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse

#
from ...forms import (
    AssetFromImagesForm,
    AssetFromNftsForm,
    AssetFromMetadataURLForm,
)
from ...models import Nft, Asset
from ...utils.ipfs import IPFSUtils

#
from ..utils.pagination import *
from ..utils.form_kwargs import PassArgumentsToForm


import boto3

S3_BASE_URL = "https://s3.us-east-1.amazonaws.com/"
BUCKET = "nftmarketgallery"


def add_asset_to_s3(asset_file):
    # photo-file will be the "name" attribute on the <input type="file">
    if asset_file:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=profile.aws_access_key_id_value,
            aws_secret_access_key=profile.aws_secret_access_key_value,
        )
        # need a unique "key" for S3 / needs image file extension too
        key = (
            uuid.uuid4().hex[:6] + asset_file.name[asset_file.name.rfind(".") :]
        )
        # just in case something goes wrong
        try:
            s3.upload_fileobj(asset_file, BUCKET, key)
            # build the full url string
            url = f"{S3_BASE_URL}/{BUCKET}/{key}"
            return url
        except:
            print("An error occurred uploading file to S3")


class AssetFromImagesCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = AssetFromImagesForm
    model = Asset
    template_name = "assets/form.html"

    #
    def get_success_url(self):
        return reverse("asset_detail", kwargs={"asset_uuid": self.object.uuid})

    #
    def post(self, request, *args, **kwargs):
        #
        form = self.form_class(
            request, self.profile, request.POST, request.FILES
        )
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        #
        asset = form.save(commit=False)
        asset.creator = self.profile
        asset.save()
        print(asset.__dict__)
        #
        # https://gateway.pinata.cloud/ipfs/QmX232ULoePr7nRBndq5Vj5kSmjAjuhdv5Gks2Uisnc3qc/_metadata.json
        ipfsutils = IPFSUtils()
        counter = 0
        for asset_file in request.FILES:
            # upload file
            nft_asset_uri = ipfsutils.pinContentToIPFS(asset_file)
            # Create metadata
            nft_metadata = {
                "name": "{}_{}".format(asset.name, counter),
                "description": asset.description,
                "asset": nft_asset_uri,
                "edition": counter,
            }
            # upload metadata
            nft_metadata_uri = ipfsutils.pinJSONToIPFS(nft_metadata)
            #
            try:
                nft = Nft(
                    name="{}_{}".format(asset.name, counter),
                    description=asset.description,
                    creator=request.user,
                    nft_type=asset.asset_type,
                    uri_metadata=nft_metadata_uri,
                    uri_asset=nft_asset_uri,
                    uri_preview=nft_asset_uri,
                )
                nft.save()
                asset.nfts.add(nft)
                print("Adding new NFT to collection: {}".format(nft.id))
            except Exception as e:
                print(e)
            #
            counter += 1
        #
        return redirect("/assets/own/")


class AssetFromNftsCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = AssetFromNftsForm
    model = Asset
    template_name = "assets/form.html"

    #
    def get_success_url(self):
        return reverse("asset_detail", kwargs={"asset_uuid": self.object.uuid})


class AssetFromMetadataURLCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = AssetFromMetadataURLForm
    model = Asset
    template_name = "assets/form.html"

    #
    def get_success_url(self):
        return reverse("asset_detail", kwargs={"asset_uuid": self.object.uuid})

    #
    def post(self, request, *args, **kwargs):
        #
        form = self.form_class(
            request, self.profile, request.POST, request.FILES
        )
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        #
        asset = form.save(commit=False)
        asset.creator = request.user
        asset.save()
        print(asset.__dict__)
        #
        # https://gateway.pinata.cloud/ipfs/QmX232ULoePr7nRBndq5Vj5kSmjAjuhdv5Gks2Uisnc3qc/_metadata.json
        #
        counter = 0
        print("Loading Metadata: ")
        asset_metadata = requests.get(asset.uri_metadata).json()
        print("Loaded Metadata: {}".format(metadata))
        nft_metadata_dir = Path(asset.uri_metadata).resolve().parent
        for nft_metadata in asset_metadata:
            nft_asset_uri = nft_metadata["image"]
            nft_asset_filename = "{}.json".format(
                Path(asset.uri_metadata).resolve().stem
            )
            nft_metadata_uri = os.path.join(
                nft_metadata_dir, nft_asset_filename
            )
            #
            try:
                nft = Nft(
                    name="{}_{}".format(asset.name, counter),
                    description=asset.description,
                    creator=request.user,
                    nft_type=asset.asset_type,
                    uri_metadata=nft_metadata_uri,
                    uri_asset=nft_asset_uri,
                    uri_preview=nft_asset_uri,
                )
                nft.save()
                asset.nfts.add(nft)
                print("Adding new NFT to collection: {}".format(nft.uuid))
            except Exception as e:
                print(e)
            #
            counter += 1
        #
        return redirect("/assets/own/")


class AssetEdit(PassArgumentsToForm, UpdateView):
    """ """

    form_class = AssetFromNftsForm
    model = Asset
    template_name = "assets/form.html"
    #
    def get_object(self, queryset=None):
        return Asset.objects.get(uuid=self.kwargs.get("asset_uuid"))

    #
    def get_success_url(self):
        return reverse("asset_detail", kwargs={"asset_uuid": self.object.uuid})

    #
    def form_valid(self, form):
        # form.instance.seller = self.profile
        return super().form_valid(form)


class AssetDelete(PassArgumentsToForm, DeleteView):
    """ """

    model = Asset
    success_url = "/assets/"
    template_name = "assets/delete.html"
    #
    def get_object(self, queryset=None):
        return Asset.objects.get(uuid=self.kwargs.get("asset_uuid"))

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        return super(AssetDelete, self).delete(*args, **kwargs)


class AssetList(PassArgumentsToForm, ListView):
    """ """

    paginate_by = 25
    model = Asset

    def get_querset(self):
        return Asset.objects.filter(seller=self.request.user)


class AssetDetailView(PassArgumentsToForm, DetailView):
    """ """

    model = Asset

    def get_querset(self):
        return Asset.objects.filter(seller=self.request.user)
