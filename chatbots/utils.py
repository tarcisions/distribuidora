import importlib
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def processar_mensagem_handler(atendimento, mensagem):
    if not atendimento.etapa_atual:
        logger.warning(f"Atendimento {atendimento.id} sem etapa atual")
        return None
    
    handler_path = atendimento.etapa_atual.handler_path
    
    try:
        module_path, class_name = handler_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        handler_class = getattr(module, class_name)
        handler = handler_class()
        
        resultado = handler.handle(atendimento, mensagem)
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao processar handler {handler_path}: {str(e)}")
        return {
            'resposta': 'Desculpe, ocorreu um erro. Por favor, tente novamente.',
            'tipo': 'text'
        }

def obter_ou_criar_atendimento(chatbot, numero_whatsapp):
    from chatbots.models import Atendimento, Etapa
    from clientes.models import Cliente
    
    lock_key = f'atendimento_{chatbot.id}_{numero_whatsapp}'
    
    if cache.get(lock_key):
        cache_atendimento_id = cache.get(lock_key)
        try:
            return Atendimento.objects.get(id=cache_atendimento_id)
        except Atendimento.DoesNotExist:
            pass
    
    atendimento = Atendimento.objects.filter(
        chatbot=chatbot,
        numero_whatsapp=numero_whatsapp,
        status='ativo'
    ).first()
    
    if not atendimento:
        cliente = Cliente.objects.filter(telefone=numero_whatsapp).first()
        
        etapa_inicial = Etapa.objects.filter(
            chatbot=chatbot,
            ativa=True
        ).order_by('ordem').first()
        
        atendimento = Atendimento.objects.create(
            chatbot=chatbot,
            cliente=cliente,
            numero_whatsapp=numero_whatsapp,
            etapa_atual=etapa_inicial,
            status='ativo'
        )
    
    cache.set(lock_key, atendimento.id, timeout=3600)
    
    return atendimento

def validar_tipo_mensagem_media(tipo_mensagem):
    tipos_invalidos = ['audio', 'image', 'document', 'video', 'sticker']
    return tipo_mensagem in tipos_invalidos
