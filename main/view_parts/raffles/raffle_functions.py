# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

#
from ..utils.pagination import *

#
from ...forms import RaffleForm
from ...models import Raffle

#
import pprint
import uuid
import requests
from requests import HTTPError
import json
import os
from pathlib import Path
import sys
import logging


@login_required
def raffles_running(request):
    #
    raffles_running = Raffle.objects.all()
    #
    context = {"page_obj": get_page_obj(request, raffles_running, 25)}
    return render(request, "raffles/list.html", context)


@login_required
def raffles_own(request):
    #
    raffles_own = Raffle.objects.filter(asset__seller=request.user)
    #
    context = {"page_obj": get_page_obj(request, raffles_own, 25)}
    return render(request, "raffles/list.html", context)


@login_required
def raffles_own_running(request):
    #
    raffles_own_running = Raffle.objects.filter(asset__seller=request.user)
    #
    context = {"page_obj": get_page_obj(request, raffles_own_running, 25)}
    return render(request, "raffles/list.html", context)


@login_required
def raffles_own_scheduled(request):
    #
    raffles_own_scheduled = Raffle.objects.filter(asset__seller=request.user)
    #
    context = {"page_obj": get_page_obj(request, raffles_own_scheduled, 25)}
    return render(request, "raffles/list.html", context)


@login_required
def raffles_own_ended(request):
    #
    raffles_own_ended = Raffle.objects.filter(asset__seller=request.user)
    #
    context = {"page_obj": get_page_obj(request, raffles_own_ended, 25)}
    return render(request, "raffles/list.html", context)


@login_required
def raffle_detail(request, raffle_uuid):
    #
    raffle = Raffle.objects.get(uuid=raffle_uuid)
    raffle_form = RaffleForm()
    #
    return render(
        request,
        "raffles/detail.html",
        {"raffle": raffle, "raffle_form": raffle_form},
    )


@login_required
def raffle_add_assets(request, raffle_uuid):
    pass


@login_required
def raffle_list_participants(request, raffle_uuid):
    pass


@login_required
def raffle_add_participants(request, raffle_uuid):
    pass
