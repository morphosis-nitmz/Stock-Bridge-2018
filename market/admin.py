from django.contrib import admin

from .models import Company, Transaction, InvestmentRecord, CompanyCMPRecord


admin.site.register(Company)
admin.site.register(Transaction)
admin.site.register(InvestmentRecord)
admin.site.register(CompanyCMPRecord)
