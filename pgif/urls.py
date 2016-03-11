from django.conf.urls import url, include
from django.contrib import admin
import rest_framework_swagger

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^convert/', include('convert.urls', namespace='convert', app_name='convert')),
]
