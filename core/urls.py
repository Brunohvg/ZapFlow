from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Configuração do Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="API para o projeto de gestão de clientes e produtos",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="brunvidal@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# URLs principais
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.apps.account.urls')),
    path('', include('core.apps.dashboard.urls')),
    path('', include('core.apps.integration.urls')),    
    
    # Tornando o Swagger a página inicial da API
    path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger como página inicial
    
    # Redoc para documentação alternativa
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Rota das APIs de usuários e produtos
    path('api/', include('core.apps.rest_api.urls')),  # Rota da API
]
