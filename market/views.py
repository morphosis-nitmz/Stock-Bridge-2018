from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View, ListView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import localtime

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Company, CompanyCMPRecord, InvestmentRecord, Transaction
from .forms import StockTransactionForm
from stock_bridge.mixins import LoginRequiredMixin, CountNewsMixin


User = get_user_model()
START_TIME = timezone.make_aware(getattr(settings, 'START_TIME'))
STOP_TIME = timezone.make_aware(getattr(settings, 'STOP_TIME'))


@login_required
def deduct_tax(request):
    if request.user.is_superuser:
        for user in User.objects.all():
            tax = user.cash * Decimal(0.4)
            user.cash -= tax
            user.save()
        return HttpResponse('success')
    return redirect('/')


@login_required
def update_market(request):
    if request.user.is_superuser:
        # update company cmp data
        company_qs = Company.objects.all()
        for company in company_qs:
            company.update_cmp()
        return HttpResponse('cmp updated')
    return redirect('/')


class CompanyCMPCreateView(View):

    def get(self, request, *args, **kwargs):
        for company in Company.objects.all():
            obj = CompanyCMPRecord.objects.create(company=company, cmp=company.cmp)
        return HttpResponse('success')


class CompanySelectionView(LoginRequiredMixin, CountNewsMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'market/select_company.html', {
            'object_list': Company.objects.all()
        })


class CompanyCMPChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None, *args, **kwargs):
        qs = CompanyCMPRecord.objects.filter(company__code=kwargs.get('code'))
        if qs.count() > 15:
            qs = qs[:15]
        qs = reversed(qs)  # reverse timestamp sorting i.e. latest data should be in front
        labels = []
        cmp_data = []
        for cmp_record in qs:
            labels.append(localtime(cmp_record.timestamp).strftime('%H:%M'))
            cmp_data.append(cmp_record.cmp)
        current_cmp = Company.objects.get(code=kwargs.get('code')).cmp
        if cmp_data[-1] != current_cmp:
            labels.append(timezone.make_aware(datetime.now()).strftime('%H:%M'))
            cmp_data.append(current_cmp)
        data = {
            "labels": labels,
            "cmp_data": cmp_data,
        }
        return Response(data)


class CompanyTransactionView(LoginRequiredMixin, CountNewsMixin, View):

    def get(self, request, *args, **kwargs):
        company = Company.objects.get(code=kwargs.get('code'))
        obj, created = InvestmentRecord.objects.get_or_create(user=request.user, company=company)
        stocks_owned = obj.stocks
        return render(request, 'market/transaction_market.html', {
            'object': company,
            'company_list': Company.objects.all(),
            'stocks_owned': stocks_owned,
            'form': StockTransactionForm()
        })

    def post(self, request, *args, **kwargs):
        company = Company.objects.get(code=kwargs.get('code'))
        current_time = timezone.make_aware(datetime.now())
        if current_time >= START_TIME and current_time <= STOP_TIME:
            user = request.user
            mode = request.POST.get('mode')
            quantity = int(request.POST.get('quantity'))
            price = company.cmp
            investment_obj, obj_created = InvestmentRecord.objects.get_or_create(user=user, company=company)
            if quantity > 0:
                if mode == 'buy':
                    purchase_amount = Decimal(quantity) * price
                    if user.cash >= purchase_amount:
                        if company.stocks_remaining >= quantity:
                            # user.buy_stocks(quantity, price)
                            # company.user_buy_stocks(quantity)
                            # investment_obj.add_stocks(quantity)
                            obj = Transaction.objects.create(
                                user=user,
                                company=company,
                                num_stocks=quantity,
                                price=price,
                                mode=mode,
                                user_net_worth=InvestmentRecord.objects.calculate_net_worth(user)
                            )
                            messages.success(request, 'Transaction Complete!')
                        else:
                            messages.error(request, 'The company does not have that many stocks left!')
                    else:
                        messages.error(request, 'Insufficient Balance for this transaction!')
                elif mode == 'sell':
                    if quantity <= investment_obj.stocks and quantity <= company.stocks_offered:
                        # user.sell_stocks(quantity, price)
                        # company.user_sell_stocks(quantity)
                        # investment_obj.reduce_stocks(quantity)
                        obj = Transaction.objects.create(
                            user=user,
                            company=company,
                            num_stocks=quantity,
                            price=price,
                            mode=mode,
                            user_net_worth=InvestmentRecord.objects.calculate_net_worth(user)
                        )
                        messages.success(request, 'Transaction Complete!')
                    else:
                        messages.error(request, 'Please enter a valid quantity!')
                else:
                    messages.error(request, 'Please enter a valid mode!')
            else:
                messages.error(request, 'The quantity cannot be negative!')
        else:
            msg = 'The market will be live from {start} to {stop}'.format(
                start=START_TIME.strftime('%H:%M'),
                stop=STOP_TIME.strftime('%H:%M')
            )
            messages.info(request, msg)
        url = reverse('market:transaction', kwargs={'code': company.code})
        return HttpResponseRedirect(url)


class UserTransactionHistoryView(LoginRequiredMixin, CountNewsMixin, ListView):
    template_name = 'market/user_transaction_history.html'

    def get_queryset(self, *args, **kwargs):
        return Transaction.objects.get_by_user(user=self.request.user)
