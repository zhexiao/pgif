from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
import rest_framework_swagger

urlpatterns = [
    url(r'^docs/', include('rest_framework_swagger.urls')),
    url(r'^convert/', include('convert.urls', namespace='convert', app_name='convert')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
