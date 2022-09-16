# Import the mixin for class-based views
from django.contrib.auth.forms import UserCreationForm
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
from ..utils.pagination import *
from ..utils.form_kwargs import PassArgumentsToForm

#
from ...models import Purchase
from ...forms import PurchaseForm
from ...utils.ipfs import IPFSUtils


class PurchaseBoughtList(PassArgumentsToForm, ListView):
    """ """

    paginate_by = 25
    model = Purchase
    form_class = PurchaseForm
    template_name = "purchases/list.html"
    #
    def get_queryset(self):
        return Purchase.objects.filter(bid__buyer=self.request.user)


class PurchaseSoldList(PassArgumentsToForm, ListView):
    """ """

    paginate_by = 25
    model = Purchase
    form_class = PurchaseForm
    template_name = "purchases/list.html"
    #
    def get_queryset(self):
        return Purchase.objects.filter(bid__auction__seller=self.request.user)


class PurchaseListJson(BaseDatatableView):
    model = Purchase
    columns = ['id', 'uuid', 'bid', 'tx_hash', 'tx_token', 'purchase_time']
    order_columns = ['id', 'uuid', 'bid', 'tx_hash', 'tx_token', 'purchase_time']

    def get_initial_queryset(self):
        return Purchase.objects.filter(bid__auction__seller=self.request.user)


class PurchaseDetailView(PassArgumentsToForm, DetailView):
    """ """

    model = Purchase
    form_class = PurchaseForm
    template_name = "purchases/detail.html"
    #
    def get_object(self, queryset=None):
        return Purchase.objects.get(uuid=self.kwargs.get("purchase_uuid"))
