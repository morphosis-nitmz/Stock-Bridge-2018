from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View, ListView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import localtime

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Company, Transaction
from .forms import CompanySelectionForm, StockTransactionForm
from record.models import CompanyCMPRecord, InvestmentRecord
from stock_bridge.mixins import LoginRequiredMixin


class CompanySelectionView(LoginRequiredMixin, View):
    form_class = CompanySelectionForm

    def get(self, request, *args, **kwargs):
        return render(request, 'market/select_company.html', {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        code = request.POST.get('company_list')
        url = reverse('market:transaction', kwargs={'code': code})
        return HttpResponseRedirect(url)


class CompanyCMPChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None, *args, **kwargs):
        qs = CompanyCMPRecord.objects.filter(company__code=kwargs.get('code'))
        if qs.count() > 10:
            qs = qs[:10]
        qs = reversed(qs)  # reverse timestamp sorting i.e. latest data should be in front
        labels = []
        cmp_data = []
        for cmp_record in qs:
            labels.append(localtime(cmp_record.timestamp).strftime('%H:%M'))
            cmp_data.append(cmp_record.cmp)
        current_cmp = Company.objects.get(code=kwargs.get('code')).cmp
        if cmp_data[-1] != current_cmp:
            labels.append(localtime(timezone.now()).strftime('%H:%M'))
            cmp_data.append(current_cmp)
        data = {
            "labels": labels,
            "cmp_data": cmp_data,
        }
        return Response(data)


class CompanyTransactionView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = Company.objects.get(code=kwargs.get('code'))
        stocks_owned = InvestmentRecord.objects.get(user=request.user, company=company).stocks
        return render(request, 'market/transaction_market.html', {
            'object': company,
            'stocks_owned': stocks_owned,
            'form': StockTransactionForm()
        })

    def post(self, request, *args, **kwargs):
        company = Company.objects.get(code=kwargs.get('code'))
        mode = request.POST.get('mode')
        quantity = int(request.POST.get('quantity'))
        obj = Transaction.objects.create(request.user, company, quantity, company.cmp, mode)
        if obj is not None:
            messages.success(request, 'Transaction complete!')
        else:
            messages.error(request, 'Please enter a valid quantity.')
        return render(request, 'market/transaction_market.html', {
            'object': company,
            'form': StockTransactionForm()
        })


class UserTransactionHistoryView(LoginRequiredMixin, ListView):
    template_name = 'market/user_transaction_history.html'

    def get_queryset(self, *args, **kwargs):
        return Transaction.objects.get_by_user(user=self.request.user)
