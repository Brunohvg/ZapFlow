from rest_framework import viewsets
from core.apps.account.models import User

# Importando serializers
from .serializers.account_serializers import UserSerializer

# ViewSet para Users
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer