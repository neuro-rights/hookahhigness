# Import the login_required decorator
from django.contrib.auth.decorators import login_required


@login_required
def opensea(request):
    pass
