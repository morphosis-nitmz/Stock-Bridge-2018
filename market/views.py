from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View, ListView
from django.core.urlresolvers import reverse
from django.contrib import messages

from .models import Company, Transaction
from .forms import CompanySelectionForm, StockTransactionForm
from stock_bridge.mixins import LoginRequiredMixin


class CompanySelectionView(LoginRequiredMixin, View):
    form_class = CompanySelectionForm

    def get(self, request, *args, **kwargs):
        return render(request, 'market/select_company.html', {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        code = request.POST.get('company_list')
        url = reverse('market:transaction', kwargs={'code': code})
        return HttpResponseRedirect(url)


class CompanyTransactionView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = Company.objects.get(code=kwargs.get('code'))
        return render(request, 'market/transaction_market.html', {
            'object': company,
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
