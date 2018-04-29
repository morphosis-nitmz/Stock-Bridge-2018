from decimal import Decimal

from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView, FormView, CreateView, View
from django.views.generic.edit import FormMixin
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from .forms import LoginForm, RegisterForm, ReactivateEmailForm
from .models import EmailActivation
from stock_bridge.mixins import AnonymousRequiredMixin, RequestFormAttachMixin, NextUrlMixin, LoginRequiredMixin
from market.models import InvestmentRecord


User = get_user_model()


class LoanView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/loan.html', {
            'user': request.user
        })

    def post(self, request, *args, **kwargs):
        mode = request.POST.get('mode')
        user = request.user
        if mode == 'issue':
            if user.issue_loan():
                messages.success(request, 'Loan has been issued.')
            else:
                messages.error(request, 'You can issue loan atmost 5 times a day!')
        elif mode == 'pay':
            if user.pay_installment():
                messages.success(request, 'Installment paid!')
            else:
                messages.error(
                    request,
                    'Minimum installment amount has to be INR 10,000 and you should have sufficient balance.'
                )
        return redirect('account:loan')


def cancel_loan(request):
    for user in User.objects.all():
        user.cancel_loan()
    return HttpResponse('Loan Deducted', status=200)


def deduct_interest(request):
    for user in User.objects.all():
        user.cancel_loan()
    return HttpResponse('Interest Deducted', status=200)


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.username != kwargs.get('username'):
            return redirect('/')
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        username = self.kwargs.get('username')
        instance = User.objects.filter(username=username).first()
        if instance is None:
            raise Http404('User not found')
        return instance

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileView, self).get_context_data(*args, **kwargs)
        qs = InvestmentRecord.objects.filter(user=self.request.user)
        if qs.count() >= 1:
            context['net_worth'] = InvestmentRecord.objects.calculate_net_worth(self.request.user)
            context['investments'] = qs
        return context


class LeaderBoardView(View):
    template_name = 'accounts/leaderboard.html'

    def get(self, request, *args, **kwargs):
        data = []
        user_qs = User.objects.all()
        for user in user_qs:
            net_worth = InvestmentRecord.objects.calculate_net_worth(user)
            data.append((user.username, net_worth, user.coeff_of_variation))
        data = sorted(data, key=lambda d: (-d[1], d[2]))
        return render(request, 'accounts/leaderboard.html', {'data': data})


class AccountEmailActivateView(FormMixin, View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    key = None

    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:  # Not confirmed but confirmable
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request, 'Your email has been confirmed! Please login to continue.')
                return redirect('login')
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    reset_link = reverse('password_reset')
                    msg = """Your email has already been confirmed.
                    Do you want to <a href="{link}">reset you password</a>?""".format(link=reset_link)
                    messages.success(request, mark_safe(msg))
                    return redirect('login')
        context = {'form': self.get_form(), 'key': key}  # get_form() works because of the mixin
        return render(request, 'registration/activation_error.html', context)

    def post(self, request, *args, **kwargs):
        # create a form to receive an email
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = 'Activation link sent. Please check your email.'
        messages.success(self.request, msg)
        email = form.cleaned_data.get('email')
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation()
        return super(AccountEmailActivateView, self).form_valid(form)

    def form_invalid(self, form):
        """
        This method had to be explicitly written because this view uses the basic django "View" class.
        If it had used some other view like ListView etc. Django would have handled it automatically.
        """
        context = {'form': form, 'key': self.key}
        return render(self.request, 'registration/activation_error.html', context)


class LoginView(AnonymousRequiredMixin, RequestFormAttachMixin, NextUrlMixin, FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'
    default_url = '/'
    default_next = '/'

    def form_valid(self, form):
        request = self.request
        response = form.cleaned_data
        if not response.get('success'):
            messages.warning(request, mark_safe(response.get('message')))
            return redirect('login')
        next_path = self.get_next_url()
        return redirect(next_path)


class RegisterView(AnonymousRequiredMixin, CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'

    def form_valid(self, form):
        super(RegisterView, self).form_valid(form)
        messages.success(self.request, 'Verification link sent! Please check your email.')
        return redirect(self.success_url)
