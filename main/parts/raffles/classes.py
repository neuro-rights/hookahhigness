from datetime import datetime, timedelta, time

# Import the mixin for class-based views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
#
from ..utils.pagination import *
from ..utils.form_kwargs import PassArgumentsToForm

#
from ...forms import RaffleForm
from ...models import Asset, Collection, Auction, Raffle


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

    def get_object(self, queryset=None):
        return Raffle.objects.get(uuid=self.kwargs.get("raffle_uuid"))

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
        form.instance.collection.seller = self.request.user
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


class RaffleOwnRunningListJson(BaseDatatableView):
    columns = ['uuid', 'collection', 'participants', 'winner', 'datetime_start', 'datetime_end', 'price_entry', 'status']
    order_columns = ['uuid', 'collection', 'participants', 'winner', 'datetime_start', 'datetime_end', 'price_entry', 'status']

    def get_initial_queryset(self):
        now = datetime.now()
        return Raffle.objects.filter(collection__seller=self.request.user, datetime_start__lte=now, datetime_end__gte=now)


class RaffleOwnScheduledListJson(BaseDatatableView):
    columns = ['uuid', 'collection', 'participants', 'winner', 'datetime_start', 'datetime_end', 'price_entry', 'status']
    order_columns = ['uuid', 'collection', 'participants', 'winner', 'datetime_start', 'datetime_end', 'price_entry', 'status']

    def get_initial_queryset(self):
        now = datetime.now()
        return Raffle.objects.filter(collection__seller=self.request.user, datetime_start__gt=now)


class RaffleOwnEndedListJson(BaseDatatableView):
    columns = ['uuid', 'collection', 'participants', 'winner', 'datetime_start', 'datetime_end', 'price_entry', 'status']
    order_columns = ['uuid', 'collection', 'participants', 'winner', 'datetime_start', 'datetime_end', 'price_entry', 'status']

    def get_initial_queryset(self):
        now = datetime.now()
        return Raffle.objects.filter(collection__seller=self.request.user, datetime_end__lt=now)


class RaffleDetailView(PassArgumentsToForm, DetailView):
    model = Raffle
    form_class = RaffleForm
    template_name = "raffles/detail.html"

    def get_object(self, queryset=None):
        return Raffle.objects.get(uuid=self.kwargs.get("raffle_uuid"))
