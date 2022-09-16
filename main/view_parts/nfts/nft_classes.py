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
from ..utils.pagination import *
from ..utils.form_kwargs import PassArgumentsToForm

#
from ...forms import NftForm
from ...models import Nft, User


class NftCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = NftForm
    model = Nft
    template_name = "nfts/form.html"
    #
    def get_success_url(self):
        return reverse("nft_detail", kwargs={"nft_uuid": self.object.uuid})


class NftEdit(PassArgumentsToForm, UpdateView):
    """ """

    form_class = NftForm
    model = Nft
    template_name = "nfts/form.html"
    #
    def get_object(self, queryset=None):
        return Nft.objects.get(uuid=self.kwargs.get("nft_uuid"))

    #
    def get_success_url(self):
        return reverse("nft_detail", kwargs={"nft_uuid": self.object.uuid})


class NftDelete(LoginRequiredMixin, DeleteView):
    """ """

    model = Nft
    success_url = "/nfts/own/"
    template_name = "nfts/delete.html"

    def get_object(self, queryset=None):
        return Nft.objects.get(uuid=self.kwargs.get("nft_uuid"))


class NftListJson(BaseDatatableView):
    model = Nft
    columns = ['id', 'uuid']
    order_columns = ['id', 'uuid']

    def get_initial_querset(self):
        return Nft.objects.filter(creator=self.request.user)


class NftList(PassArgumentsToForm, ListView):
    """ """

    paginate_by = 25
    model = Nft
    form_class = NftForm
    template_name = "nfts/list.html"
    #
    def get_queryset(self):
        return Nft.objects.filter(creator=self.request.user)


class NftDetailView(PassArgumentsToForm, DetailView):
    """ """

    model = Nft
    form_class = NftForm
    template_name = "nfts/detail.html"
    #
    def get_object(self, queryset=None):
        return Nft.objects.get(uuid=self.kwargs.get("nft_uuid"))
