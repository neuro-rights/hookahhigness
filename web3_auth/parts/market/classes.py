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

#
from ...forms import AuctionForm
from ...models import Auction


class MarketList(ListView):
    """ """

    paginate_by = 25
    model = Auction
    fields = [
        "description",
        "collections",
        "blockchain",
        "time_start",
        "time_end",
        "bid_start_value",
        "status",
    ]
    template_name = "market/list.html"
    #
    def get_queryset(self):
        return Auction.objects.all()
