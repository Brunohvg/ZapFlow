from rest_framework.routers import DefaultRouter
from .views import UserViewSet
# Criando o router
router = DefaultRouter()
router.register(r'users', UserViewSet)
#router.register(r'dashboard', DashboardViewSet)
#router.register(r'integrations', IntegrationViewSet)

# URLs
urlpatterns = router.urls
