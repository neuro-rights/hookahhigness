# Import the login_required decorator
from django.contrib.auth.decorators import login_required

# Import the mixin for class-based views
from django.contrib.auth import login
from django.contrib.auth import logout

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
        form = UserCreate(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "User created successfully")
            form = UserEditForm(instance=user)
            context = {"form": form}
            return render(request, "registration/profile.html", context)
    #
    form = UserCreateForm()
    context = {"form": form}
    #
    return render(request, "registration/signup.html", context)

def custom_login(request):
    if request.user.is_authenticated:
        return redirect("moralis_auth")

    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
                return redirect("moralis_auth")

        else:
            for error in list(form.errors.values()):
                messages.error(request, error) 

    form = AuthenticationForm() 
    
    return render(
        request=request,
        template_name="users/login.html", 
        context={'form': form}
        )

@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("moralis_auth")


@login_required
def profile(request):
    #
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "User upated successfully")
            context = {"form": form}
            return render(request, "registration/profile.html", context)
    #
    form = UserEditForm(instance=request.user)
    context = {"form": form}
    return render(request, "registration/profile.html", context)


@login_required
def followers(request):
    pass
