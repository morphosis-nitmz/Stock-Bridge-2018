from django.db import models
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


class Transaction(models.Model):
    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
    num_stocks = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    mode = models.CharField(max_length=10, choices=TRANSACTION_MODES)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{user}: {company} - {time}'.format(
            user=self.user.username, company=self.company.name, time=self.timestamp
        )
