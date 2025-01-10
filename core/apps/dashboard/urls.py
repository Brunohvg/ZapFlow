from django.urls import path

from core.apps.dashboard import views

app_name = 'dashboard'


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),  # noqa E501

]