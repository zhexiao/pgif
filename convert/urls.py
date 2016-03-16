from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^video\/?$', ConvertVideo.as_view()),
    url(r'^app\/?$', HomeView.as_view(), name='home'),
]