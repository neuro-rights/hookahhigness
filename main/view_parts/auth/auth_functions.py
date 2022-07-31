# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.contrib.auth import login
from django.contrib import messages

# Import the mixin for class-based views
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

#
from ...forms import UserCreateForm, UserEditForm
from ...models import User

#
from ..utils.pagination import *


def signup(request):
    #
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "User created successfully")
            form = UserEditForm()
            context = {"form": form}
            return render(request, "registration/profile.html", context)
    #
    form = UserCreateForm()
    context = {"form": form}
    #
    return render(request, "registration/signup.html", context)


@login_required
def profile(request):
    #
    if request.method == "POST":
        form = UserEditForm(request.POST)
        if not form.is_valid():
            context = {"form": form}
            return render(request, "registration/profile.html", context)
        form.save()
        messages.success(request, "Profile successfully")
    #
    form = UserEditForm()
    context = {"form": form}
    return render(request, "registration/profile.html", context)


@login_required
def followers(request):
    pass
