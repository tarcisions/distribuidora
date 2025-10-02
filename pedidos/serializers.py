from rest_framework import serializers
from .models import Produto, Pedido

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'
        read_only_fields = ['criado_em', 'atualizado_em']

class PedidoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    
    class Meta:
        model = Pedido
        fields = '__all__'
        read_only_fields = ['criado_em', 'atualizado_em', 'valor_total']
