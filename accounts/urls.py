from django.conf.urls import url

from .views import AccountEmailActivateView, LoanView, cancel_loan, deduct_interest


urlpatterns = [
    url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', AccountEmailActivateView.as_view(), name='email-activate'),
    url(r'^email/resend-activation/$', AccountEmailActivateView.as_view(), name='resend-activation'),
    url(r'^bank/loan$', LoanView.as_view(), name='loan'),
    url(r'^bank/loan/deduct$', cancel_loan, name='cancel_loan'),
    url(r'^bank/interest/deduct$', deduct_interest, name='deduct_interest'),
]
