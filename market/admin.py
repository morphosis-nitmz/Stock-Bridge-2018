from django.contrib import admin

from .models import Company, InvestmentRecord, CompanyCMPRecord, Transaction


admin.site.register(Company)
admin.site.register(Transaction)
admin.site.register(InvestmentRecord)
admin.site.register(CompanyCMPRecord)
