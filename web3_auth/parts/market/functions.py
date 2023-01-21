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
from ...models import Auction


def market_list(request):
    return render(request, "market/list.html")


@login_required
def market_own(request):
    return render(request, "market/list.html")
