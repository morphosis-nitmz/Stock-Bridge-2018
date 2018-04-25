from decimal import Decimal

from django.db import models
from django.db.models.signals import pre_save
from django.contrib.auth import get_user_model


User = get_user_model()

TRANSACTION_MODES = (
    ('buy', 'BUY'),
    ('sell', 'SELL')
)


class Company(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=20, unique=True)
    cap = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    stocks_offered = models.IntegerField(default=0)
    stocks_remaining = models.IntegerField(default=stocks_offered)
    cmp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def user_buy_stocks(self, quantity):
        self.stocks_remaining -= quantity
        self.cmp = self.cmp / Decimal(2.0) + (self.cmp * quantity) / self.stocks_offered
        self.save()

    def user_sell_stocks(self, quantity):
        self.stocks_remaining += quantity
        self.cmp = self.cmp / Decimal(2.0) - (self.cmp * quantity) / self.stocks_offered
        self.save()


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

    def create(self, user, company, num_stocks, price, mode):
        # check for negative quantity
        if mode == 'buy':
            if num_stocks > company.stocks_remaining:
                return None
            company.user_buy_stocks(num_stocks)
            user.buy_stocks(num_stocks, price)
        elif mode == 'sell':
            if num_stocks * company.cmp > user.net_worth:
                return None
            company.user_sell_stocks(num_stocks)
            user.sell_stocks(num_stocks, price)
        obj = Transaction(user=user, company=company, num_stocks=num_stocks, price=price, mode=mode)
        if obj is not None:
            obj.save(force_insert=True)
        return obj


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
