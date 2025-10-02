from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'estado', 'cidade']
    search_fields = ['nome', 'cpf_cnpj', 'telefone']
    ordering_fields = ['nome', 'criado_em', 'ultima_interacao']
    ordering = ['-criado_em']
