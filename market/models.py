from decimal import Decimal

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth import get_user_model
from django.urls import reverse


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
    cap = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)  # Company's worth
    cmp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    change = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Company's change in cmp w.r.t last price
    stocks_offered = models.IntegerField(default=0)
    stocks_remaining = models.IntegerField(default=stocks_offered)
    cap_type = models.CharField(max_length=20, choices=CAP_TYPES, blank=True, null=True)
    industry = models.CharField(max_length=120, blank=True, null=True)
    temp_stocks_bought = models.IntegerField(default=0)  # Refresh after every CMP update
    temp_stocks_sold = models.IntegerField(default=0)  # Refresh after every CMP update
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['cap_type', 'code']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """ URL for user market transaction """
        return reverse('market:transaction', kwargs={'code': self.code})

    def get_absolute_admin_url(self):
        """ URL for admin change """
        return reverse('market:admin', kwargs={'code': self.code})

    def get_cap(self):
        cap = self.cap_type
        if cap == 'small':
            return 'Small Cap'
        if cap == 'mid':
            return 'Mid Cap'
        return 'Large Cap'

    def calculate_change(self, old_price):
        """ Calculate CMP change """
        print('old', old_price)
        self.change = ((self.cmp - old_price) / old_price) * Decimal(100.00)
        print(self.change)
        self.save()

    def update_cmp(self):
        old_price = self.cmp
        self.cmp += (
            self.cmp * Decimal(self.temp_stocks_bought) - self.cmp * Decimal(self.temp_stocks_sold)
        ) / Decimal(self.stocks_offered)
        self.calculate_change(old_price)
        self.temp_stocks_bought = 0
        self.temp_stocks_sold = 0
        self.save()

    def user_buy_stocks(self, quantity):
        if quantity <= self.stocks_remaining:
            self.stocks_remaining -= quantity
            self.temp_stocks_bought += quantity
            self.save()
            return True
        return False

    def user_sell_stocks(self, quantity):
        if quantity <= self.stocks_offered:
            self.stocks_remaining += quantity
            self.temp_stocks_sold += quantity
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
    user_net_worth = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)  # user's net worth after current transaction
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
    amount = InvestmentRecord.objects.calculate_net_worth(instance.user)
    instance.user_net_worth = amount

    # transaction completion reflection in other models
    investment_obj, obj_created = InvestmentRecord.objects.get_or_create(
        user=instance.user, company=instance.company
    )
    if instance.mode == 'buy':
        instance.user.buy_stocks(instance.num_stocks, instance.price)
        instance.company.user_buy_stocks(instance.num_stocks)
        investment_obj.add_stocks(instance.num_stocks)
    elif instance.mode == 'sell':
        instance.user.sell_stocks(instance.num_stocks, instance.price)
        instance.company.user_sell_stocks(instance.num_stocks)
        investment_obj.reduce_stocks(instance.num_stocks)

pre_save.connect(pre_save_transaction_receiver, sender=Transaction)


def post_save_transaction_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        # changes to user model
        net_worth_list = [
            transaction.user_net_worth for transaction in Transaction.objects.filter(user=instance.user)
        ]
        instance.user.update_cv(net_worth_list)

post_save.connect(post_save_transaction_create_receiver, sender=Transaction)


class InvestmentRecordQuerySet(models.query.QuerySet):

    def get_by_user(self, user):
        return self.filter(user=user)

    def get_by_company(self, company):
        return self.filter(company=company)


class InvestmentRecordManager(models.Manager):

    def get_queryset(self):
        return InvestmentRecordQuerySet(self.model, using=self._db)

    def get_by_user(self, user):
        return self.get_queryset().get_by_user(user=user)

    def get_by_company(self, company):
        return self.get_queryset().get_by_company(company=company)

    def calculate_net_worth(self, user):
        qs = self.get_by_user(user)
        amount = Decimal(0.00)
        for inv in qs:
            amount += Decimal(inv.stocks) * inv.company.cmp
        return amount + user.cash


class InvestmentRecord(models.Model):
    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
    stocks = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)

    objects = InvestmentRecordManager()

    class Meta:
        unique_together = ('user', 'company')

    def __str__(self):
        return self.user.username + ' - ' + self.company.code

    def add_stocks(self, num_stocks):
        self.stocks += num_stocks
        self.save()

    def reduce_stocks(self, num_stocks):
        if self.stocks >= num_stocks:
            self.stocks -= num_stocks
            self.save()


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        for company in Company.objects.all():
            obj = InvestmentRecord.objects.create(user=instance, company=company)

post_save.connect(post_save_user_create_receiver, sender=User)


class CompanyCMPRecord(models.Model):
    """ This model is used for keeping record of company's cmp in order to use Chart.js """
    company = models.ForeignKey(Company)
    cmp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.company.code
