from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import View

from .models import BankAccount
from stock_bridge.mixins import LoginRequiredMixin


class BankLoanView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        account = BankAccount.objects.get(user=request.user)
        return render(request, 'bank/loan.html', {
            'user': request.user,
            'account': account
        })

    def post(self, request, *args, **kwargs):
        mode = request.POST.get('mode')
        bank_account = BankAccount.objects.get(user=request.user)
        if mode == 'issue':
            bank_account.issue_loan()
            messages.success(request, 'Loan has been issued.')
        elif mode == 'pay':
            if bank_account.get_installment():
                messages.success(request, 'Installment paid!')
            else:
                messages.error(
                    request,
                    'Minimum installment amount has to be INR 10,000 and you should have sufficient balance.'
                )
        return redirect('bank:loan')


def deduct_loan(request):
    bank_account = BankAccount.objects.get(user=request.user)
    bank_account.withdraw_loan()
    return HttpResponse('Loan Deducted', status=200)


def deduct_interest(request):
    bank_account = BankAccount.objects.get(user=request.user)
    bank_account.deduct_interest()
    return HttpResponse('Interest Deducted', status=200)
