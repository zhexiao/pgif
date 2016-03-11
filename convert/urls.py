from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^video/(?P<link>[^\*]+)$', ConvertVideo.as_view()),
]