from django.conf.urls import url

from .views import CompanySelectionView, CompanyTransactionView


urlpatterns = [
    url(r'^select/$', CompanySelectionView.as_view(), name='company_select'),
    url(r'^transact/(?P<code>\w+)$', CompanyTransactionView.as_view(), name='transaction'),
]
