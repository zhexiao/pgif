import datetime

from django.shortcuts import render
from django.views.generic import View


class HomeView(View):

    def get(self, request):
        now = datetime.datetime.now()

        return render(request, 'convert/index.html', {
            'section': 'index',
            'current_year': now.year
        })
