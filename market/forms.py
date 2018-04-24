from django import forms

from .models import Company, TRANSACTION_MODES


class CompanySelectionForm(forms.Form):
    company_list = forms.ChoiceField(choices=[
        (company.code, company.name) for company in Company.objects.all()
    ])


class StockTransactionForm(forms.Form):
    mode = forms.ChoiceField(choices=TRANSACTION_MODES)
    quantity = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'pattern': '[0-9]+',
        'title': 'Enter integers only',
        'placeholder': 'Enter integers only'
    }))
