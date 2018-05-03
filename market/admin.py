from django.contrib import admin

from .models import Company, InvestmentRecord, CompanyCMPRecord


admin.site.register(Company)
admin.site.register(InvestmentRecord)
admin.site.register(CompanyCMPRecord)
