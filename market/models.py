import numpy as np
from decimal import Decimal

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth import get_user_model


User = get_user_model()

TRANSACTION_MODES = (
    ('buy', 'BUY'),
    ('sell', 'SELL')
)

CAP_TYPES = (
    ('small', 'Small Cap'),
    ('mid', 'Mid Cap'),
    ('large', 'Large Cap')
)


class Company(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=20, unique=True)
    cap = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    cmp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    change = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stocks_offered = models.IntegerField(default=0)
    stocks_remaining = models.IntegerField(default=0)
    cap_type = models.CharField(max_length=20, choices=CAP_TYPES, blank=True, null=True)
    industry = models.CharField(max_length=120, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def calculate_change(self, old_price):
        self.change = ((self.cmp - old_price) / old_price) * Decimal(100.00)
        self.save()

    def user_buy_stocks(self, quantity):
        if quantity <= self.stocks_remaining:
            self.stocks_remaining -= quantity
            self.cmp = self.cmp / Decimal(2.0) + (self.cmp * Decimal(quantity)) / Decimal(self.stocks_offered)
            self.save()
            return True
        return False

    def user_sell_stocks(self, quantity):
        if quantity <= self.stocks_offered:
            self.stocks_remaining += quantity
            self.cmp = self.cmp / Decimal(2.0) - (self.cmp * Decimal(quantity)) / Decimal(self.stocks_offered)
            self.save()
            return True
        return False


def pre_save_company_receiver(sender, instance, *args, **kwargs):
    if instance.cmp <= Decimal(0.00):
        instance.cmp = Decimal(0.01)

pre_save.connect(pre_save_company_receiver, sender=Company)


def post_save_company_receiver(sender, instance, created, *args, **kwargs):
    if created:
        user_qs = User.objects.all()
        for user in user_qs:
            obj, create = InvestmentRecord.objects.get_or_create(user=user, company=instance)

post_save.connect(post_save_company_receiver, sender=Company)


class TransactionQuerySet(models.query.QuerySet):

    def get_by_user(self, user):
        return self.filter(user=user)

    def get_by_company(self, company):
        return self.filter(company=company)

    def get_by_user_and_company(self, user, company):
        return self.get_by_user(user).get_by_company(company)


class TransactionManager(models.Manager):

    def get_queryset(self):
        return TransactionQuerySet(self.model, using=self._db)

    def get_by_user(self, user):
        return self.get_queryset().get_by_user(user)

    def get_by_company(self, company):
        return self.get_queryset().get_by_company(company)

    def get_by_user_and_company(self, user, company):
        return self.get_queryset().get_by_user_and_company(user, company)


class Transaction(models.Model):
    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
    num_stocks = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    mode = models.CharField(max_length=10, choices=TRANSACTION_MODES)
    user_net_worth = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = TransactionManager()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return '{user}: {company} - {time}'.format(
            user=self.user.username, company=self.company.name, time=self.timestamp
        )


def pre_save_transaction_receiver(sender, instance, *args, **kwargs):
    instance.user_net_worth = instance.user.net_worth

pre_save.connect(pre_save_transaction_receiver, sender=Transaction)


def post_save_transaction_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        # changes to investment model
        investment_obj, obj_created = InvestmentRecord.objects.get_or_create(
            user=instance.user, company=instance.company
        )
        if instance.mode == 'buy':
            investment_obj.stocks += instance.num_stocks
        elif instance.mode == 'sell':
            investment_obj.stocks -= instance.num_stocks
        investment_obj.save()

        # changes to user model
        net_worth_list = [
            transaction.user_net_worth for transaction in Transaction.objects.filter(user=instance.user)
        ]
        instance.user.update_cv(net_worth_list)

post_save.connect(post_save_transaction_create_receiver, sender=Transaction)


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


class CompanyCMPRecord(models.Model):
    company = models.ForeignKey(Company)
    cmp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.company.code
