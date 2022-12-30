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
from ...forms import AssetForm
from ...models import Asset, User


class AssetCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = AssetForm
    model = Asset
    template_name = "assets/form.html"
    #
    def get_success_url(self):
        return reverse("asset_detail", kwargs={"asset_uuid": self.object.uuid})


class AssetEdit(PassArgumentsToForm, UpdateView):
    """ """

    form_class = AssetForm
    model = Asset
    template_name = "assets/form.html"
    #
    def get_object(self, queryset=None):
        return Asset.objects.get(uuid=self.kwargs.get("asset_uuid"))

    #
    def get_success_url(self):
        return reverse("asset_detail", kwargs={"asset_uuid": self.object.uuid})


class AssetDelete(LoginRequiredMixin, DeleteView):
    """ """

    model = Asset
    success_url = "/assets/own/"
    template_name = "assets/delete.html"

    def get_object(self, queryset=None):
        return Asset.objects.get(uuid=self.kwargs.get("asset_uuid"))


class AssetListJson(BaseDatatableView):
    model = Asset
    columns = ['uuid', 'asset_type', 'creator', 'name']
    order_columns = ['asset_type', 'uuid', 'creator', 'name']

    def get_initial_querset(self):
        return Asset.objects.filter(creator=self.request.user)


class AssetList(PassArgumentsToForm, ListView):
    """ """

    paginate_by = 25
    model = Asset
    form_class = AssetForm
    template_name = "assets/list.html"
    #
    def get_queryset(self):
        return Asset.objects.filter(creator=self.request.user)


class AssetDetailView(PassArgumentsToForm, DetailView):
    """ """

    model = Asset
    form_class = AssetForm
    template_name = "assets/detail.html"
    #
    def get_object(self, queryset=None):
        return Asset.objects.get(uuid=self.kwargs.get("asset_uuid"))
