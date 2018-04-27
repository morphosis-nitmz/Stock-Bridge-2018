from django_cron import CronJobBase, Schedule

from .models import CompanyCMPRecord
from market.models import Company


class CronCreateCMPRecord(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'record.create_cmp_record'    # a unique code

    def do(self):
        for company in Company.objects.all():
            obj = CompanyCMPRecord.objects.create(company=company, cmp=company.cmp)
