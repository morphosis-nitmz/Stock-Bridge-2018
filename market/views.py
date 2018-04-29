from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View, ListView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import localtime

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Company, Transaction, CompanyCMPRecord, InvestmentRecord
from .forms import StockTransactionForm
from stock_bridge.mixins import LoginRequiredMixin


class CompanyCMPCreateView(View):

    def get(self, request, *args, **kwargs):
        for company in Company.objects.all():
            obj = CompanyCMPRecord.objects.create(company=company, cmp=company.cmp)
        return HttpResponse('success')


class CompanySelectionView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'market/select_company.html', {
            'object_list': Company.objects.all()
        })


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
        obj, created = InvestmentRecord.objects.get_or_create(user=request.user, company=company)
        stocks_owned = obj.stocks
        return render(request, 'market/transaction_market.html', {
            'object': company,
            'stocks_owned': stocks_owned,
            'form': StockTransactionForm()
        })

    def post(self, request, *args, **kwargs):
        company = Company.objects.get(code=kwargs.get('code'))
        mode = request.POST.get('mode')
        quantity = int(request.POST.get('quantity'))
        price = company.cmp
        user = request.user
        if quantity > 0:
            if mode == 'buy':
                if user.buy_stocks(quantity, price):
                    if company.user_buy_stocks(quantity):
                        obj = Transaction.objects.create(
                            user=user,
                            company=company,
                            num_stocks=quantity,
                            price=price,
                            mode=mode,
                            user_net_worth=InvestmentRecord.objects.calculate_net_worth(user)
                        )
                        company.calculate_change(price)
                        messages.success(request, 'Transaction Complete!')
                    else:
                        messages.error(request, 'The company does not have that many stocks left!')
                else:
                    messages.error(request, 'You cannot make a purchase of value more than your net worth!')
            elif mode == 'sell':
                investment_obj = InvestmentRecord.objects.get(user=user, company=company)
                if quantity <= investment_obj.stocks and company.user_sell_stocks(quantity):
                    user.sell_stocks(quantity, price)
                    obj = Transaction.objects.create(
                        user=user,
                        company=company,
                        num_stocks=quantity,
                        price=price,
                        mode=mode,
                        user_net_worth=InvestmentRecord.objects.calculate_net_worth(user)
                    )
                    company.calculate_change(price)
                    messages.success(request, 'Transaction Complete!')
                else:
                    messages.error(request, 'Please enter a valid quantity!')
            else:
                messages.error(request, 'Please enter a valid mode!')
        else:
            messages.error(request, 'The quantity cannot be negative!')
        url = reverse('market:transaction', kwargs={'code': company.code})
        return HttpResponseRedirect(url)


class UserTransactionHistoryView(LoginRequiredMixin, ListView):
    template_name = 'market/user_transaction_history.html'

    def get_queryset(self, *args, **kwargs):
        return Transaction.objects.get_by_user(user=self.request.user)
