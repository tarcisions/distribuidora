from rest_framework import serializers
from .models import Chatbot, Etapa, Atendimento, Mensagem

class ChatbotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatbot
        fields = '__all__'
        read_only_fields = ['criado_em', 'atualizado_em']
        extra_kwargs = {
            'meta_access_token': {'write_only': True}
        }

class EtapaSerializer(serializers.ModelSerializer):
    chatbot_nome = serializers.CharField(source='chatbot.nome', read_only=True)
    
    class Meta:
        model = Etapa
        fields = '__all__'

class AtendimentoSerializer(serializers.ModelSerializer):
    chatbot_nome = serializers.CharField(source='chatbot.nome', read_only=True)
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    etapa_nome = serializers.CharField(source='etapa_atual.nome', read_only=True)
    
    class Meta:
        model = Atendimento
        fields = '__all__'
        read_only_fields = ['iniciado_em', 'finalizado_em', 'atualizado_em']

class MensagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensagem
        fields = '__all__'
        read_only_fields = ['criada_em']
