from django.contrib import admin
from .models import Chatbot, Etapa, Atendimento, Mensagem

@admin.register(Chatbot)
class ChatbotAdmin(admin.ModelAdmin):
    list_display = ['nome', 'numero_telefone', 'ativo', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'numero_telefone']
    readonly_fields = ['criado_em', 'atualizado_em']
    ordering = ['nome']

@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ['chatbot', 'codigo', 'nome', 'ordem', 'ativa']
    list_filter = ['chatbot', 'ativa']
    search_fields = ['codigo', 'nome']
    ordering = ['chatbot', 'ordem']

@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'chatbot', 'numero_whatsapp', 'cliente', 'etapa_atual', 'status', 'iniciado_em']
    list_filter = ['chatbot', 'status', 'iniciado_em']
    search_fields = ['numero_whatsapp', 'cliente__nome']
    readonly_fields = ['iniciado_em', 'finalizado_em', 'atualizado_em']
    ordering = ['-iniciado_em']

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ['id', 'atendimento', 'direcao', 'tipo', 'processada', 'criada_em']
    list_filter = ['direcao', 'tipo', 'processada', 'criada_em']
    search_fields = ['conteudo', 'meta_message_id']
    readonly_fields = ['criada_em']
    ordering = ['-criada_em']
