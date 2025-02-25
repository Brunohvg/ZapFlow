from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Criando o router
router = DefaultRouter()
router.register(r'users', UserViewSet)
#router.register(r'produtos', ProdutoViewSet)  # Rota para produto

# URLs da API
urlpatterns = [
    path('', include(router.urls)),
    
]
