from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('core.apps.account.urls')),
    path('',include('core.apps.dashboard.urls')),
    path('api/',include('core.apps.rest_api.urls')),

]

