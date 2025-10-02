from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf_cnpj', 'telefone', 'cidade', 'estado', 'status', 'ultima_interacao']
    list_filter = ['status', 'estado', 'cidade']
    search_fields = ['nome', 'cpf_cnpj', 'telefone']
    readonly_fields = ['criado_em', 'atualizado_em', 'ultima_interacao']
    ordering = ['-criado_em']
