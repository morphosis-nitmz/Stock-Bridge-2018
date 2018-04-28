from django.conf.urls import url

from .views import CompanySelectionView, CompanyTransactionView, CompanyCMPChartData


urlpatterns = [
    url(r'^select/$', CompanySelectionView.as_view(), name='company_select'),
    url(r'^transact/(?P<code>\w+)$', CompanyTransactionView.as_view(), name='transaction'),
    url(r'^company/api/(?P<code>\w+)$', CompanyCMPChartData.as_view(), name='cmp_api_data'),
]
