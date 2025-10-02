from django.db import models

class ConfiguracaoIntegracao(models.Model):
    TIPO_CHOICES = [
        ('api_externa', 'API Externa'),
        ('banco_direto', 'Acesso Direto ao Banco'),
        ('webhook', 'Webhook'),
        ('outro', 'Outro'),
    ]

    nome = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, db_index=True)
    url_base = models.URLField(blank=True)
    credenciais = models.JSONField(default=dict)
    headers_padrao = models.JSONField(default=dict)
    ativa = models.BooleanField(default=True, db_index=True)
    configuracoes_extras = models.JSONField(default=dict)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configuracoes_integracao'
        verbose_name = 'Configuração de Integração'
        verbose_name_plural = 'Configurações de Integração'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

class LogIntegracao(models.Model):
    configuracao = models.ForeignKey(
        ConfiguracaoIntegracao,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    metodo = models.CharField(max_length=20)
    endpoint = models.CharField(max_length=500)
    payload_enviado = models.JSONField(default=dict)
    resposta_recebida = models.JSONField(default=dict)
    status_code = models.IntegerField(null=True)
    sucesso = models.BooleanField(default=False, db_index=True)
    erro = models.TextField(blank=True)
    tempo_resposta_ms = models.IntegerField(null=True)
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'logs_integracao'
        verbose_name = 'Log de Integração'
        verbose_name_plural = 'Logs de Integração'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['configuracao', 'criado_em']),
            models.Index(fields=['sucesso', 'criado_em']),
        ]

    def __str__(self):
        return f"{self.metodo} {self.endpoint} - {'Sucesso' if self.sucesso else 'Erro'}"
