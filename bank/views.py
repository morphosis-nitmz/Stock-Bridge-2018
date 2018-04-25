from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import View

from .models import BankAccount
from stock_bridge.mixins import LoginRequiredMixin


class IssueLoanView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'bank/loan.html', {'user': request.user})

    def post(self, request, *args, **kwargs):
        bank_account = BankAccount.objects.get(user=request.user)
        bank_account.issue_loan()
        messages.success(request, 'Loan has been issued.')
        return redirect('bank:issue_loan')


def deduct_loan(request):
    bank_account = BankAccount.objects.get(user=request.user)
    bank_account.withdraw_loan()
    return HttpResponse('Deducted', status=200)
