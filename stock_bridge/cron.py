from django.contrib.auth import get_user_model
from django_cron import CronJobBase, Schedule

from market.models import CompanyCMPRecord, Company


User = get_user_model()


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
        for user in User.objects.all():
            user.deduct_interest()
