# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
#
from ..utils.pagination import *
from ..utils.form_kwargs import PassArgumentsToForm

#
from ...forms import RaffleForm
from ...models import Nft, Asset, Auction, Raffle


class RaffleCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = RaffleForm
    model = Raffle
    template_name = "raffles/form.html"

    def get_form(self):
        form = super().get_form()
        form.fields['datetime_start'].widget = DateTimePickerInput()
        form.fields['datetime_end'].widget = DateTimePickerInput()
        return form
    #
    def get_success_url(self):
        return reverse(
            "raffle_detail", kwargs={"raffle_uuid": self.object.uuid}
        )


class RaffleEdit(PassArgumentsToForm, UpdateView):
    """ """

    form_class = RaffleForm
    model = Raffle
    template_name = "raffles/form.html"

    def get_form(self):
        form = super().get_form()
        form.fields['datetime_start'].widget = DateTimePickerInput()
        form.fields['datetime_end'].widget = DateTimePickerInput()
        return form
    #
    def get_success_url(self):
        return reverse(
            "raffle_detail", kwargs={"raffle_uuid": self.object.uuid}
        )

    #
    def form_valid(self, form):
        form.instance.asset.seller = self.request.user
        return super().form_valid(form)


class RaffleDelete(LoginRequiredMixin, DeleteView):
    """ """

    model = Raffle
    success_url = "/raffles/own/"
    template_name = "raffles/delete.html"

    def get_object(self, queryset=None):
        return Raffle.objects.get(uuid=self.kwargs.get("raffle_uuid"))

class RaffleList(PassArgumentsToForm, ListView):
    """ """

    paginate_by = 25
    model = Raffle
    template_name = "raffles/list.html"
    #
    def get_queryset(self):
        return Raffle.objects.all()

class RaffleDetailView(PassArgumentsToForm, DetailView):
    model = Raffle
