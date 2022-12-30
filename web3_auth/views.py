import json
import requests

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

API_KEY = 'LccUHRDHRPyQSZX17ll8hrU5kuAiKcsDXSnPxyFCKNuDzjC2Wg45Lau4gIuxbGE2'
if API_KEY == 'WEB3_API_KEY_HERE':
    print("API key is not set")
    raise SystemExit

from datetime import datetime, timedelta, time

from django.shortcuts import render

from .models import Collection

from .parts.utils.pagination import *
from .parts.utils.form_kwargs import *
from .parts.auth.functions import *
from .parts.assets.classes import *
from .parts.assets.functions import *
from .parts.collections.classes import *
from .parts.collections.functions import *
from .parts.bids.classes import *
from .parts.bids.functions import *
from .parts.auctions.classes import *
from .parts.auctions.functions import *
from .parts.purchases.classes import *
from .parts.raffles.classes import *
from .parts.raffles.functions import *

# from .view_parts.opensea.opensea import *
from .parts.market.classes import *
from .parts.market.functions import *

"""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

class HomeView(PassArgumentsToForm, generics.ListCreateAPIView):
    paginate_by = 25
    model = Auction
    form_class = AuctionForm
    template_name = "home.html"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        now = datetime.now()
        return Auction.objects.filter(datetime_start__lte=now, datetime_end__gte=now)
"""

def home(request):
    #
    now = datetime.now()
    auctions_list = Auction.objects.filter(datetime_start__lte=now, datetime_end__gte=now)
    context = {"page_obj": get_page_obj(request, auctions_list, 25)}
    return render(request, "home.html", context)


def opensea(request):
    pass


def tickets(request):
    pass


def about(request):
    pass


def help(request):
    return render(request, 'help/index.html')

def room(request, room_name):
    return render(request, 'help/room.html', {
        'room_name': room_name
    })

def moralis_auth(request):
    now = datetime.now()
    auctions_list = Auction.objects.filter(datetime_start__lte=now, datetime_end__gte=now)
    context = {"page_obj": get_page_obj(request, auctions_list, 25)}
    return render(request, "home.html", context)
    #return render(request, 'login.html', {})

def my_profile(request):
    return render(request, 'profile.html', {})

def request_message(request):
    data = json.loads(request.body)
    print(data)

    REQUEST_URL = 'https://authapi.moralis.io/challenge/request/evm'
    request_object = {
      "domain": "defi.finance",
      "chainId": 1,
      "address": data['address'],
      "statement": "Please confirm",
      "uri": "https://defi.finance/",
      "expirationTime": "2023-01-01T00:00:00.000Z",
      "notBefore": "2020-01-01T00:00:00.000Z",
      "timeout": 15
    }
    x = requests.post(
        REQUEST_URL,
        json=request_object,
        headers={'X-API-KEY': API_KEY})

    return JsonResponse(json.loads(x.text))


def verify_message(request):
    data = json.loads(request.body)
    print(data)

    REQUEST_URL = 'https://authapi.moralis.io/challenge/verify/evm'
    x = requests.post(
        REQUEST_URL,
        json=data,
        headers={'X-API-KEY': API_KEY})
    print(json.loads(x.text))
    print(x.status_code)
    if x.status_code == 201:
        # user can authenticate
        eth_address=json.loads(x.text).get('address')
        print("eth address", eth_address)
        try:
            user = User.objects.get(username=eth_address)
        except User.DoesNotExist:
            user = User(username=eth_address)
            user.is_staff = False
            user.is_superuser = False
            user.save()
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['auth_info'] = data
                request.session['verified_data'] = json.loads(x.text)
                return JsonResponse({'user': user.username})
            else:
                return JsonResponse({'error': 'account disabled'})
    else:
        return JsonResponse(json.loads(x.text))


