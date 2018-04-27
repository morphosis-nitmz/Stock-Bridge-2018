from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from market.models import Company, Transaction


User = get_user_model()


class InvestmentRecord(models.Model):
    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
    stocks = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'company')

    def __str__(self):
        return self.user.username + ' - ' + self.company.code


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        for company in Company.objects.all():
            obj = InvestmentRecord.objects.create(user=instance, company=company)

post_save.connect(post_save_user_create_receiver, sender=User)


def post_save_transaction_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        investment_obj = InvestmentRecord.objects.filter(user=instance.user, company=instance.company).first()
        investment_obj.stocks = instance.num_stocks
        investment_obj.save()

post_save.connect(post_save_transaction_create_receiver, sender=Transaction)


class CompanyCMPRecord(models.Model):
    company = models.ForeignKey(Company)
    cmp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company.code
