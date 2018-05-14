from datetime import datetime, timedelta

from django.conf import settings
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url

from .decorators import login_required_message_and_redirect
from market.models import Company, CompanyCMPRecord
from accounts.models import News


class CountNewsMixin(object):
    """ Count current news amount for display in navbar """

    def dispatch(self, request, *args, **kwargs):
        request.session['news'] = News.objects.filter(is_active=True).count()
        return super(CountNewsMixin, self).dispatch(request, *args, **kwargs)


class AdminRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return super(AdminRequiredMixin, self).dispatch(request, *args, **kwargs)
        return redirect(getattr(settings, 'LOGIN_URL_REDIRECT', '/'))


class LoginRequiredMixin(object):
    """ This mixin ensures that only logged in users can access the page """

    @method_decorator(login_required_message_and_redirect)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class AnonymousRequiredMixin(object):
    """ This mixin ensures that logged in users cannot access the page """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(getattr(settings, 'LOGIN_URL_REDIRECT', '/'))
        return super(AnonymousRequiredMixin, self).dispatch(request, *args, **kwargs)


class RequestFormAttachMixin(object):
    """ This method is overridden to send additional data from the view to the form.
        In function based view, this can be done as "form = LoginForm(request=request)"
    """

    def get_form_kwargs(self):
        kwargs = super(RequestFormAttachMixin, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class NextUrlMixin(object):
    default_next = '/'

    def get_next_url(self):
        request = self.request
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if is_safe_url(redirect_path, request.get_host()):
            return redirect_path
        return self.default_next
