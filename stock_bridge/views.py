from django.shortcuts import render
from django.views.generic import View

from .mixins import CountNewsMixin


class HomeView(CountNewsMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'home.html', {})

    def post(self, request, *args, **kwargs):
        return render(request, 'home.html', {})


def instruction_view(request):
    return render(request, 'instructions.html', {})
