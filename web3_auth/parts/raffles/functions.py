# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core import serializers
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
def raffles_own_running(request):
    #
    return render(request, "raffles/list_running.html")


@login_required
def raffles_own_scheduled(request):
    #
    return render(request, "raffles/list_scheduled.html")


@login_required
def raffles_own_ended(request):
    #
    return render(request, "raffles/list_ended.html")


@login_required
def raffle_detail(request, raffle_uuid):
    #
    raffle = Raffle.objects.get(uuid=raffle_uuid)
    return render(
        request, "raffles/detail.html", {"raffle": raffle}
    )


@login_required
def raffle_add_collections(request, raffle_uuid):
    pass


@login_required
def raffle_list_participants(request, raffle_uuid):
    pass


@login_required
def raffle_add_participants(request, raffle_uuid):
    pass
