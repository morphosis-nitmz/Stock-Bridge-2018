from django.conf.urls import url

from .views import IssueLoanView, deduct_loan, deduct_interest


urlpatterns = [
    url(r'^issue/$', IssueLoanView.as_view(), name='issue_loan'),
    url(r'^deduct/loan$', deduct_loan, name='deduct_loan'),
    url(r'^deduct/interest$', deduct_interest, name='deduct_interest'),
]
