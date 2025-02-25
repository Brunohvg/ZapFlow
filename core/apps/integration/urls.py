from django.urls import path

from core.apps.integration import views

app_name = 'integration'


urlpatterns = [
    path('integracao/', views.integration, name='integration'),  # noqa E501
    path('integracao/whatsapp/', views.whatsapp, name='whatsapp'),  # noqa E501
    path('integracao/nuvemshop/', views.nuvemshop, name='nuvemshop'),  # noqa E501


]

