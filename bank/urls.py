from django.conf.urls import url

from .views import BankLoanView, deduct_loan, deduct_interest


urlpatterns = [
    url(r'^loan/$', BankLoanView.as_view(), name='loan'),
    url(r'^deduct/loan$', deduct_loan, name='deduct_loan'),
    url(r'^deduct/interest$', deduct_interest, name='deduct_interest'),
]
