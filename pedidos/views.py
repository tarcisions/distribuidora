from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Produto, Pedido
from .serializers import ProdutoSerializer, PedidoSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'disponibilidade']
    search_fields = ['nome', 'categoria', 'descricao']
    ordering_fields = ['nome', 'preco', 'criado_em']
    ordering = ['categoria', 'nome']

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'cliente']
    search_fields = ['cliente__nome', 'cliente__cpf_cnpj']
    ordering_fields = ['criado_em', 'valor_total', 'status']
    ordering = ['-criado_em']
