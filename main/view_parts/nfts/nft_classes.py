# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse

#
from ..utils.pagination import *
from ..utils.form_kwargs import PassArgumentsToForm

#
from ...forms import NftForm
from ...models import Nft, User


class NftCreate(LoginRequiredMixin, CreateView):
    """ """

    form_class = NftForm
    model = Nft
    template_name = "nfts/form.html"
    #
    def get_success_url(self):
        return reverse("nft_detail", kwargs={"nft_uuid": self.object.uuid})


class NftEdit(LoginRequiredMixin, UpdateView):
    """ """

    form_class = NftForm
    model = Nft
    template_name = "nfts/form.html"
    #
    def get_object(self, queryset=None):
        return Auction.objects.get(uuid=self.kwargs.get("nft_uuid"))

    #
    def get_success_url(self):
        return reverse("nft_detail", kwargs={"nft_uuid": self.object.uuid})


class NftDelete(LoginRequiredMixin, DeleteView):
    """ """

    model = Nft
    success_url = "/nfts/own"
    template_name = "nfts/delete.html"


class NftList(LoginRequiredMixin, ListView):
    """ """

    paginate_by = 25
    model = Nft
    template_name = "nfts/list.html"
    #
    def get_queryset(self):
        return Nft.objects.filter(creator=self.request.user)


class NftDetailView(LoginRequiredMixin, DetailView):
    """ """

    model = Nft
    #
    def get_queryset(self):
        return Nft.objects.filter(creator=self.request.user)
