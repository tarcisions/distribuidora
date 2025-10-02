from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=200)
    cpf_cnpj = models.CharField(max_length=20, unique=True, db_index=True)
    estado = models.CharField(max_length=50)
    cidade = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')],
        default='ativo',
        db_index=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ultima_interacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.nome} ({self.cpf_cnpj})"
