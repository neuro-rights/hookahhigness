# Import the login_required decorator
from django.contrib.auth.decorators import login_required

from django.core.exceptions import SuspiciousOperation
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse


def get_page_obj(request, list_to_paginate, max_items_per_page):
    paginator = Paginator(list_to_paginate, per_page=max_items_per_page)
    page_number = request.GET.get("page")
    #
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # if the page is out of range, deliver the last page
        page_obj = paginator.page(paginator.num_pages)
    #
    # page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_number)
    #
    return page_obj
