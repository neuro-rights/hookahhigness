from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin


class PassArgumentsToForm(LoginRequiredMixin, FormMixin):
    #
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)

    def get_form_kwargs(self):
        kwargs = super(PassArgumentsToForm, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs
