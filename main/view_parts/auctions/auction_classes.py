# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django.utils.decorators import method_decorator
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

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

    def get_form(self):
        form = super().get_form()
        form.fields['datetime_start'].widget = DateTimePickerInput()
        form.fields['datetime_end'].widget = DateTimePickerInput()
        return form
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

    def get_form(self):
        form = super().get_form()
        form.fields['datetime_start'].widget = DateTimePickerInput()
        form.fields['datetime_end'].widget = DateTimePickerInput()
        return form
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


class AuctionDelete(LoginRequiredMixin, DeleteView):
    """ """

    model = Auction
    success_url = "/auctions/own/"
    template_name = "auctions/delete.html"
    #
    def get_object(self, queryset=None):
        return Auction.objects.get(uuid=self.kwargs.get("auction_uuid"))


class AuctionListJson(BaseDatatableView):
    model = Auction
    columns = ['id', 'uuid', 'seller', 'assets', 'blockchain', 'datetime_start', 'datetime_end', 'bid_start_value', 'bid_current_value']
    order_columns = ['id', 'uuid', 'seller', 'assets', 'blockchain', 'datetime_start', 'datetime_end', 'bid_start_value', 'bid_current_value']

    def get_initial_querset(self):
        return Auction.objects.filter(seller=self.request.user)


@method_decorator(login_required, name='dispatch')
class AuctionDetailView(PassArgumentsToForm, DetailView):
    model = Auction
    form_class = AuctionForm
    template_name = "auctions/detail.html"

    def get_object(self, queryset=None):
        return Auction.objects.get(uuid=self.kwargs.get("auction_uuid"))
