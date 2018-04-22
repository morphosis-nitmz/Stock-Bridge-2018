from django.conf.urls import url

from .views import AccountEmailActivateView


urlpatterns = [
    url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', AccountEmailActivateView.as_view(), name='email-activate'),
    url(r'^email/resend-activation/$', AccountEmailActivateView.as_view(), name='resend-activation')
]
