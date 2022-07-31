# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse

#
from ...forms import AuctionForm
from ...models import Auction

#
from ..utils.pagination import *
from ..utils.form_kwargs import PassArgumentsToForm

#
from ...utils.nft import NFTUtils
from ...utils.contract import ContractUtils


class AuctionCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = AuctionForm
    model = Auction
    template_name = "auctions/form.html"
    #
    def get_success_url(self):
        return reverse(
            "auction_detail", kwargs={"auction_uuid": self.object.uuid}
        )


class AuctionEdit(PassArgumentsToForm, UpdateView):
    """ """

    form_class = AuctionForm
    model = Auction
    template_name = "auctions/form.html"
    #
    def get_object(self, queryset=None):
        return Auction.objects.get(uuid=self.kwargs.get("auction_uuid"))

    #
    def get_success_url(self):
        return reverse(
            "auction_detail", kwargs={"auction_uuid": self.object.uuid}
        )

    #
    def form_valid(self, form):
        # form.instance.creator = self.profile
        return super().form_valid(form)


class AuctionDelete(PassArgumentsToForm, DeleteView):
    """ """

    model = Auction
    success_url = "/market/own"
    template_name = "auction/delete.html"
    #
    def get_object(self, queryset=None):
        return Auction.objects.get(uuid=self.kwargs.get("auction_uuid"))


class AuctionList(PassArgumentsToForm, CreateView):
    """ """

    paginate_by = 25
    model = Auction
    fields = [
        "description",
        "assets",
        "blockchain",
        "time_start",
        "time_end",
        "bid_start_value",
        "status",
    ]
    template_name = "auctions/list.html"
    #
    def get_queryset(self):
        return Auction.objects.filter(seller=self.request.user)


class AuctionDetailView(PassArgumentsToForm, DetailView):
    model = Auction
