from django.contrib import admin
from .models import Produto, Pedido

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'preco', 'disponibilidade', 'criado_em']
    list_filter = ['categoria', 'disponibilidade']
    search_fields = ['nome', 'categoria', 'descricao']
    readonly_fields = ['criado_em', 'atualizado_em']
    ordering = ['categoria', 'nome']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'valor_total', 'status', 'criado_em']
    list_filter = ['status', 'criado_em']
    search_fields = ['cliente__nome', 'cliente__cpf_cnpj']
    readonly_fields = ['criado_em', 'atualizado_em', 'valor_total']
    ordering = ['-criado_em']
