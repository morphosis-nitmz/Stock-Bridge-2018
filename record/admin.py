from django.contrib import admin

from .models import InvestmentRecord, CompanyCMPRecord


admin.site.register(InvestmentRecord)
admin.site.register(CompanyCMPRecord)
