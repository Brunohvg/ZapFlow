from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from core.apps.account.models import User

class Integration(models.Model):
    TIPO_INTEGRACAO_CHOICES = [
        ('nuvemshop', 'Nuvemshop'),
        ('whatsapp', 'WhatsApp'),
        ('outro', 'Outro'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integrations')
    nome = models.CharField(max_length=100, null=True, blank=True)
    tipo = models.CharField(max_length=50, choices=TIPO_INTEGRACAO_CHOICES)
    api_url = models.URLField(null=True, blank=True)
    api_key = models.CharField(max_length=255, null=True, blank=True)
    webhook_url = models.URLField(null=True, blank=True)
    configuracoes_extras = models.JSONField(default=dict, blank=True)
    ativo = models.BooleanField(default=True, db_index=True)
    ultima_sincronizacao = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'tipo', 'nome')  # Evita duplicatas para o mesmo usuário e tipo

    def clean(self):
        """Valida o JSONField para garantir que seja um dicionário válido."""
        if not isinstance(self.configuracoes_extras, dict):
            raise ValidationError("O campo configuracoes_extras deve ser um dicionário JSON válido.")

    def is_connected(self):
        """Verifica se a instância do WhatsApp está conectada."""
        return self.configuracoes_extras.get('connected', False)

    def sync_required(self):
        """Verifica se a sincronização é necessária (caso tenha passado mais de 1 hora)."""
        if not self.ultima_sincronizacao:
            return True
        return (now() - self.ultima_sincronizacao).total_seconds() > 3600  # 1 hora

    def __str__(self):
        return self.nome or f"Integration {self.pk}"
