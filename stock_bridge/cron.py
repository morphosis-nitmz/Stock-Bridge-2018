from django_cron import CronJobBase, Schedule

from record.models import CompanyCMPRecord
from market.models import Company
from bank.models import BankAccount


class CronCreateCMPRecord(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'record.create_cmp_record'    # a unique code

    def do(self):
        for company in Company.objects.all():
            obj = CompanyCMPRecord.objects.create(company=company, cmp=company.cmp)


class CronLoanInterestDeduct(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'bank.deduct_interest'    # a unique code

    def do(self):
        for account in BankAccount.objects.all():
            account.deduct_interest()
