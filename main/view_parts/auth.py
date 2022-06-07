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
import pprint
import uuid
import requests
from requests import HTTPError
import json
import os
from pathlib import Path
import sys
import logging

#
from ..forms import ProfileForm
from ..models import Profile

from .pagination import *


def signup(request):
    #
    error_message = ""
    #
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/accounts/settings")
        else:
            error_message = "Invalid sign up - try again"
    #
    form = UserCreationForm()
    context = {"form": form, "error_message": error_message}
    #
    return render(request, "registration/signup.html", context)


@login_required
def settings(request):
    #
    error_message = ""
    #
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if not form.is_valid():
            context = {"form": form, "error_message": error_message}
            return render(request, "registration/settings.html", context)
        form.save()
    #
    form = ProfileForm()
    context = {"form": form, "error_message": error_message}
    return render(request, "registration/settings.html", context)
