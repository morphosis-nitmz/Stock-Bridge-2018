from django import forms

from .models import TRANSACTION_MODES


class StockTransactionForm(forms.Form):
    """ Form for users to make stocks transaction """
    mode = forms.ChoiceField(choices=TRANSACTION_MODES)
    quantity = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'pattern': '[0-9]+',
        'title': 'Enter integers only',
        'placeholder': 'Enter integers only'
    }))


class CompanyChangeForm(forms.Form):
    """ Form for admin to change company's CMP """
    price = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'pattern': '[0-9]+',
        'title': 'Enter integers only',
        'placeholder': 'Enter integers only'
    }))
