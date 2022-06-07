# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.urls import reverse

#
from .forms import BidForm, SellForm, FileFieldForm, NFTCollectionForm, ProfileForm
from .models import NFT, NFTCollection, Photo, Sell, Bid, Profile

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

from .view_parts.pagination import *
from .view_parts.auth import *
from .view_parts.nft import *
from .view_parts.nftcollection import *
from .view_parts.sale import *
from .view_parts.raffle import *
from .view_parts.opensea import *


def search_result(request):
    #
    if request.method == "GET":
        searched = request.GET["searched"]
        search_result = NFT.objects.filter(nft_name__contains=searched)
        #
        context = {"searched": searched, "search_result": search_result}
        return render(request, "main/nft_search_result.html", context)
    else:
        return render(request, "main/nft_search_result.html")


def home(request):
    #
    collections_list = NFTCollection.objects.order_by("-id").all()
    context = {"page_obj": get_page_obj(request, collections_list, 25)}
    return render(request, "home.html", context)
