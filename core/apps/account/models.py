from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email deve ser fornecido.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)  # Use email diretamente
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    objects = CustomUserManager()
    email = models.EmailField(max_length=255, unique=True)  # Usando o campo email padrão e tornando-o único
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_email = models.EmailField(blank=True, null=True)
    business_phone = models.CharField(max_length=20, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = "email"  # Define o campo email como identificador principal
    REQUIRED_FIELDS = []  # Campos obrigatórios adicionais (nenhum além do email)

    def save(self, *args, **kwargs):
        # Define o username como o valor de full_name, se necessário
        self.username = self.email or ''  # Caso full_name esteja em branco
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email