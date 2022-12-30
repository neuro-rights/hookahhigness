from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect

"""
from ..models import Profile

def profile_required(function):
    def wrapper(request, *args, **kwargs):
        decorated_view_func = login_required(request)
        if not decorated_view_func.user.is_authenticated():
            return decorated_view_func(request)  # return redirect to signin

        profile = Profile.objects.order_by("-id").filter(user=request.user).first()
        if not profile:  # if not coach redirect to home page
            return HttpResponseRedirect(reverse("accounts/profile/", args=(), kwargs={}))
        else:
            return function(request, *args, profile=profile, **kwargs)

    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper
"""
