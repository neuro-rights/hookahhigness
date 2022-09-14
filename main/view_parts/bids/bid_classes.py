# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from django.urls import reverse

#
from ...utils.nft import NFTUtils
from ...utils.contract import ContractUtils

#
from ..utils.pagination import *
from ..utils.form_kwargs import PassArgumentsToForm

#
from ...forms import BidForm
from ...models import Bid, Purchase


class BidList(PassArgumentsToForm, ListView):
    """ """

    paginate_by = 25
    model = Bid
    form_class = BidForm
    template_name = "bids/list.html"
    #
    def get_queryset(self):
        return Bid.objects.filter(buyer=self.request.user)


class BidDetailView(PassArgumentsToForm, DetailView):
    """ """

    model = Bid
    #
    def get_queryset(self):
        return Bid.objects.filter(buyer=self.request.user)
