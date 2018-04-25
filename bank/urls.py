from django.conf.urls import url

from .views import IssueLoanView, deduct_loan


urlpatterns = [
    url(r'^issue/$', IssueLoanView.as_view(), name='issue_loan'),
    url(r'^deduct/$', deduct_loan, name='deduct_loan'),
]
