from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model


User = get_user_model()

DEFAULT_LOAN_AMOUNT = getattr(settings, 'DEFAULT_LOAN_AMOUNT', Decimal(10000.00))


class BankAccount(models.Model):
    user = models.OneToOneField(User)
    loan = models.DecimalField(max_digits=20, decimal_places=2, default=DEFAULT_LOAN_AMOUNT)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def issue_loan(self):
        self.loan += DEFAULT_LOAN_AMOUNT
        self.save()
        self.user.net_worth += DEFAULT_LOAN_AMOUNT
        self.user.save()

    def withdraw_loan(self):
        self.user.net_worth -= self.loan
        self.user.save()
        self.loan = 0
        self.save()


def user_created_post_save_receiver(sender, instance, created, *args, **kwargs):
    if created:
        BankAccount.objects.get_or_create(user=instance)

post_save.connect(user_created_post_save_receiver, sender=User)
