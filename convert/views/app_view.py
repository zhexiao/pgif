from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

class HomeView(View):
    def get(self, request):
        return render(request, 'convert/index.html', {
            'section' : 'index'
        })