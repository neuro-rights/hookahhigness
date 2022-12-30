import datetime
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class HookahHignessMiddleware(MiddlewareMixin):
    """ """

    def _init_(self, get_response):
        self.get_response = get_response

    def _call_(self, request):
        # Code that is executed in each request before the view is called
        response = self.get_response(request)
        # Code that is executed in each request after the view is called
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        pass

    def process_exception(self, request, exception):
        # This code is executed if an exception is raised
        pass

    def process_template_response(self, request, response):
        # This code is executed if the response contains a render() method
        return response

    def process_request(self, request):
        """
        current_user = request.user
        if request.user.is_authenticated:
            now = datetime.datetime.now()
            cache.set("seen_%s" % (current_user.username), now, settings.USER_LASTSEEN_TIMEOUT)
        """
        pass
