from datetime import timedelta
from decimal import Decimal
import numpy as np

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import get_template

from stock_bridge.utils import unique_key_generator


DEFAULT_ACTIVATION_DAYS = getattr(settings, 'DEFAULT_ACTIVATION_DAYS', 7)
DEFAULT_LOAN_AMOUNT = getattr(settings, 'DEFAULT_LOAN_AMOUNT', Decimal(10000.00))
RATE_OF_INTEREST = getattr(settings, 'RATE_OF_INTEREST', Decimal(0.15))
MAX_LOAN_ISSUE = getattr(settings, 'MAX_LOAN_ISSUE')


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, full_name=None, is_active=True, is_staff=False, is_superuser=False):
        if not username:
            raise ValueError('Users must have a unique username.')
        if not email:
            raise ValueError('Users must have an email.')
        if not password:
            raise ValueError('Users must have a password.')

        user_obj = self.model(
            username=username,
            email=self.normalize_email(email),
            full_name=full_name
        )
        user_obj.set_password(password)
        user_obj.is_active = is_active
        user_obj.staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.cash = 0.00
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, username, email, full_name=None, password=None):
        user = self.create_user(
            username,
            email,
            password=password,
            full_name=full_name,
            is_staff=True
        )
        return user

    def create_superuser(self, username, email, full_name=None, password=None):
        user = self.create_user(
            username,
            email,
            password=password,
            full_name=full_name,
            is_staff=True,
            is_superuser=True
        )
        return user


class User(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=120)
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    cash = models.DecimalField(max_digits=20, decimal_places=2, default=DEFAULT_LOAN_AMOUNT)
    loan = models.DecimalField(max_digits=20, decimal_places=2, default=DEFAULT_LOAN_AMOUNT)
    loan_count = models.IntegerField(default=1)  # For arithmetic interest calculation
    loan_count_absolute = models.IntegerField(default=1)  # For overall loan issue count
    coeff_of_variation = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)  # For tie breaker in leaderboard
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        ordering = ['-cash', 'coeff_of_variation']

    def __str__(self):
        return self.username

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, object=None):
        """ Does the user have a specific permission? """
        return True

    def has_module_perms(self, app_label):
        """ Does the user have permissions to view the app 'app_label'? """
        return True

    @property
    def is_staff(self):
        return self.staff

    def buy_stocks(self, quantity, price):
        purchase_amount = Decimal(quantity) * price
        if self.cash >= purchase_amount:
            self.cash -= Decimal(quantity) * price
            self.save()
            return True
        return False

    def sell_stocks(self, quantity, price):
        self.cash += Decimal(quantity) * price
        self.save()

    def issue_loan(self):
        if self.loan_count_absolute < MAX_LOAN_ISSUE:
            self.loan_count += 1
            self.loan_count_absolute += 1
            self.loan += DEFAULT_LOAN_AMOUNT
            self.cash += DEFAULT_LOAN_AMOUNT
            self.save()
            return True
        return False

    def pay_installment(self):
        if self.loan >= DEFAULT_LOAN_AMOUNT and self.cash >= DEFAULT_LOAN_AMOUNT and self.loan_count > 0:
            self.loan_count -= 1
            self.loan -= DEFAULT_LOAN_AMOUNT
            self.cash -= DEFAULT_LOAN_AMOUNT
            self.save()
            return True
        return False

    def cancel_loan(self):
        self.loan_count = 0
        self.loan_count_absolute = 0
        self.cash = self.cash - self.loan
        self.loan = Decimal(0.00)
        self.save()

    def deduct_interest(self):
        amount = (self.loan * (Decimal(1.0) + RATE_OF_INTEREST))  # After 1 year
        compound_interest = abs(amount - self.loan)
        self.cash -= compound_interest
        self.save()

    def update_cv(self, net_worth_list):
        self.coeff_of_variation = Decimal(np.std(net_worth_list) / np.mean(net_worth_list))
        self.save()


class EmailActivationQuerySet(models.query.QuerySet):

    def confirmable(self):
        """
        Returns those emails which can be confirmed i.e. which are not activated and expired
        """
        now = timezone.now()
        start_range = now - timedelta(days=DEFAULT_ACTIVATION_DAYS)
        end_range = now
        return self.filter(activated=False, forced_expire=False).filter(
            timestamp__gt=start_range, timestamp__lte=end_range
        )


class EmailActivationManager(models.Manager):

    def get_queryset(self):
        return EmailActivationQuerySet(self.model, using=self._db)

    def confirmable(self):
        return self.get_queryset().confirmable()

    def email_exists(self, email):
        """
        EmailActivation is created when the user is created. When only EmailActivation is deleted, User object
        still remains i.e. email still exists. But this function will send nothing because for this function
        self.get_queryset() is None. So both user and EmailActivation should exist together for this to work.
        """
        return self.get_queryset().filter(
            Q(email=email) | Q(user__email=email)
        ).filter(activated=False)


class EmailActivation(models.Model):
    user = models.ForeignKey(User, on_delete=True)
    email = models.EmailField()
    key = models.CharField(max_length=120, blank=True, null=True)  # activation key
    activated = models.BooleanField(default=False)
    forced_expire = models.BooleanField(default=False)  # link expired manually
    expires = models.IntegerField(default=7)  # automatic expire (after days)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = EmailActivationManager()

    def __str__(self):
        return self.email

    def can_activate(self):
        qs = EmailActivation.objects.filter(pk=self.pk).confirmable()
        if qs.exists():
            return True
        return False

    def activate(self):
        if self.can_activate():
            user = self.user
            user.is_active = True
            user.save()
            self.activated = True
            self.save()
            return True
        return False

    def send_activation(self):
        if not self.activated and not self.forced_expire:
            if self.key:
                base_url = getattr(settings, 'HOST_SCHEME') + getattr(settings, 'BASE_URL')
                key_path = reverse('account:email-activate', kwargs={'key': self.key})
                path = '{base}{path}'.format(base=base_url, path=key_path)
                context = {
                    'path': path,
                    'email': self.email
                }
                txt_ = get_template('registration/emails/verify.txt').render(context)
                html_ = get_template('registration/emails/verify.html').render(context)
                subject = 'Morphosis Stock Bridge - Verify your Account'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [self.email]
                sent_mail = send_mail(
                    subject,
                    txt_,  # If content_type is text/plain
                    from_email,
                    recipient_list,
                    html_message=html_,  # If content_type is text/html
                    fail_silently=False  # If false, then an email will be sent if error occurs while sending the email
                )
                return sent_mail
        return False


def pre_save_email_activation_receiver(sender, instance, *args, **kwargs):
    if not instance.activated and not instance.forced_expire and not instance.key:
        instance.key = unique_key_generator(instance)

pre_save.connect(pre_save_email_activation_receiver, sender=EmailActivation)


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        email_obj = EmailActivation.objects.create(user=instance, email=instance.email)
        email_obj.send_activation()

post_save.connect(post_save_user_create_receiver, sender=User)


class News(models.Model):
    title = models.CharField(max_length=120)
    content = models.TextField()
    is_active = models.BooleanField(default=True)  # Inactive news won't appear in dashboard
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp', '-updated']

    def __str__(self):
        return self.title
