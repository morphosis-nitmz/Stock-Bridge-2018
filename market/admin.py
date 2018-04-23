from django.contrib import admin

from .models import Company, Transaction


admin.site.register(Company)
admin.site.register(Transaction)
