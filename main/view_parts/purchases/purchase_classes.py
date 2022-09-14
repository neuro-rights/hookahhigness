# Import the mixin for class-based views
from django.contrib.auth.forms import UserCreationForm
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


class PurchaseDetailView(PassArgumentsToForm, DetailView):
    """ """

    model = Purchase
    #
    def get_queryset(self):
        return Purchase.objects.filter(asset__seller=self.request.user)
