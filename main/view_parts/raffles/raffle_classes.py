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
from ...forms import RaffleForm
from ...models import Nft, Asset, Auction, Raffle


class RaffleCreate(PassArgumentsToForm, CreateView):
    """ """

    form_class = RaffleForm
    model = Raffle
    template_name = "raffles/form.html"

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

    #
    def get_success_url(self):
        return reverse(
            "raffle_detail", kwargs={"raffle_uuid": self.object.uuid}
        )

    #
    def form_valid(self, form):
        form.instance.asset.seller = self.profile
        return super().form_valid(form)


class RaffleDelete(PassArgumentsToForm, DeleteView):
    """ """

    model = Raffle
    success_url = "/raffles/"
    template_name = "raffles/delete.html"


class RaffleList(PassArgumentsToForm, ListView):
    """ """

    paginate_by = 25
    model = Raffle
    template_name = "raffles/list.html"
    #
    def get_queryset(self):
        return Raffle.objects.all()
