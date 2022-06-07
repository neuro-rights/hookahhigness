# Import the login_required decorator
from django.contrib.auth.decorators import login_required

from .pagination import *


@login_required
def add_raffle(request, collection_id):
    pass


@login_required
def raffle_detail(request, raffle_id):
    pass
