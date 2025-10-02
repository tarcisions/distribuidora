from django.db import models
from chatbots.models import Chatbot
from clientes.models import Cliente
from pedidos.models import Pedido

class MetricaContato(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, related_name='metricas_contato')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    numero_whatsapp = models.CharField(max_length=20, db_index=True)
    tipo_interacao = models.CharField(max_length=50, db_index=True)
    data_hora = models.DateTimeField(auto_now_add=True, db_index=True)
    detalhes = models.JSONField(default=dict)

    class Meta:
        db_table = 'metricas_contato'
        verbose_name = 'Métrica de Contato'
        verbose_name_plural = 'Métricas de Contato'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['chatbot', 'data_hora']),
            models.Index(fields=['tipo_interacao', 'data_hora']),
        ]

    def __str__(self):
        return f"{self.tipo_interacao} - {self.numero_whatsapp} - {self.data_hora}"

class MetricaPedido(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, related_name='metricas_pedido')
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, db_index=True)
    data_hora = models.DateTimeField(auto_now_add=True, db_index=True)
    detalhes = models.JSONField(default=dict)

    class Meta:
        db_table = 'metricas_pedido'
        verbose_name = 'Métrica de Pedido'
        verbose_name_plural = 'Métricas de Pedido'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['chatbot', 'data_hora']),
            models.Index(fields=['status', 'data_hora']),
        ]

    def __str__(self):
        return f"Pedido {self.pedido.id} - R$ {self.valor} - {self.data_hora}"

class MetricaVenda(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, related_name='metricas_venda')
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    data_venda = models.DateTimeField(auto_now_add=True, db_index=True)
    detalhes = models.JSONField(default=dict)

    class Meta:
        db_table = 'metricas_venda'
        verbose_name = 'Métrica de Venda'
        verbose_name_plural = 'Métricas de Venda'
        ordering = ['-data_venda']
        indexes = [
            models.Index(fields=['chatbot', 'data_venda']),
        ]

    def __str__(self):
        return f"Venda {self.pedido.id} - R$ {self.valor_total} - {self.data_venda}"

class MetricaReativacao(models.Model):
    chatbot = models.ForeignKey(Chatbot, on_delete=models.CASCADE, related_name='metricas_reativacao')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero_whatsapp = models.CharField(max_length=20)
    mensagem_enviada = models.TextField()
    sucesso = models.BooleanField(default=False, db_index=True)
    resposta_cliente = models.TextField(blank=True)
    data_envio = models.DateTimeField(auto_now_add=True, db_index=True)
    detalhes = models.JSONField(default=dict)

    class Meta:
        db_table = 'metricas_reativacao'
        verbose_name = 'Métrica de Reativação'
        verbose_name_plural = 'Métricas de Reativação'
        ordering = ['-data_envio']
        indexes = [
            models.Index(fields=['chatbot', 'data_envio']),
            models.Index(fields=['sucesso', 'data_envio']),
        ]

    def __str__(self):
        return f"Reativação {self.cliente.nome} - {'Sucesso' if self.sucesso else 'Pendente'} - {self.data_envio}"
