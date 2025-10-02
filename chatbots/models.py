from django.db import models
from clientes.models import Cliente

class Chatbot(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    numero_telefone = models.CharField(max_length=20, unique=True)
    meta_phone_number_id = models.CharField(max_length=100, unique=True)
    meta_business_account_id = models.CharField(max_length=100)
    meta_access_token = models.CharField(max_length=500)
    meta_app_secret = models.CharField(max_length=500, blank=True)
    verify_token = models.CharField(max_length=255, unique=True)
    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chatbots'
        verbose_name = 'Chatbot'
        verbose_name_plural = 'Chatbots'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.numero_telefone})"

class Etapa(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, related_name='etapas')
    codigo = models.CharField(max_length=50, db_index=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    handler_path = models.CharField(max_length=200)
    ordem = models.IntegerField(default=0)
    ativa = models.BooleanField(default=True)

    class Meta:
        db_table = 'etapas'
        verbose_name = 'Etapa'
        verbose_name_plural = 'Etapas'
        ordering = ['chatbot', 'ordem']
        unique_together = [['chatbot', 'codigo']]

    def __str__(self):
        return f"{self.chatbot.nome} - {self.nome}"

class Atendimento(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, related_name='atendimentos')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='atendimentos', null=True, blank=True)
    numero_whatsapp = models.CharField(max_length=20, db_index=True)
    etapa_atual = models.ForeignKey(Etapa, on_delete=models.PROTECT, null=True, blank=True)
    contexto = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo', db_index=True)
    iniciado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'atendimentos'
        verbose_name = 'Atendimento'
        verbose_name_plural = 'Atendimentos'
        ordering = ['-iniciado_em']
        indexes = [
            models.Index(fields=['chatbot', 'numero_whatsapp', 'status']),
        ]

    def __str__(self):
        return f"Atendimento {self.id} - {self.numero_whatsapp}"

class Mensagem(models.Model):
    TIPO_CHOICES = [
        ('text', 'Texto'),
        ('interactive', 'Interativo'),
        ('image', 'Imagem'),
        ('audio', 'Áudio'),
        ('document', 'Documento'),
        ('video', 'Vídeo'),
        ('location', 'Localização'),
        ('contacts', 'Contatos'),
        ('sticker', 'Sticker'),
        ('button', 'Botão'),
        ('unknown', 'Desconhecido'),
    ]

    DIRECAO_CHOICES = [
        ('recebida', 'Recebida'),
        ('enviada', 'Enviada'),
    ]

    atendimento = models.ForeignKey(Atendimento, on_delete=models.CASCADE, related_name='mensagens')
    meta_message_id = models.CharField(max_length=100, unique=True, db_index=True)
    direcao = models.CharField(max_length=20, choices=DIRECAO_CHOICES, db_index=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='text')
    conteudo = models.TextField()
    payload_completo = models.JSONField(default=dict)
    processada = models.BooleanField(default=False, db_index=True)
    enviada_com_sucesso = models.BooleanField(default=False, db_index=True)
    erro = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mensagens'
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['criada_em']
        indexes = [
            models.Index(fields=['atendimento', 'criada_em']),
            models.Index(fields=['processada', 'criada_em']),
        ]

    def __str__(self):
        return f"{self.direcao} - {self.tipo} - {self.criada_em}"
