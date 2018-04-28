from django_cron import CronJobBase, Schedule

from market.models import CompanyCMPRecord, Company
from bank.models import BankAccount


class CronCreateCMPRecord(CronJobBase):
    RUN_EVERY_MINS = 5
    ALLOW_PARALLEL_RUNS = True

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'market.create_cmp_record'    # a unique code

    def do(self):
        for company in Company.objects.all():
            obj = CompanyCMPRecord.objects.create(company=company, cmp=company.cmp)


class CronLoanInterestDeduct(CronJobBase):
    RUN_EVERY_MINS = 30
    ALLOW_PARALLEL_RUNS = True

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'market.deduct_interest'    # a unique code

    def do(self):
        for account in BankAccount.objects.all():
            account.deduct_interest()
