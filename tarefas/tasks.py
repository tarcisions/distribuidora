from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import requests
import logging
from django.conf import settings
from django.core.cache import cache
import time

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def enviar_mensagem_whatsapp(self, chatbot_id, numero_destino, mensagem, tipo='text'):
    from chatbots.models import Chatbot
    
    try:
        chatbot = Chatbot.objects.get(id=chatbot_id)
        
        url = f"{settings.WHATSAPP_API_URL}/{chatbot.meta_phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {chatbot.meta_access_token}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': numero_destino,
            'type': tipo,
        }
        
        if tipo == 'text':
            payload['text'] = {'body': mensagem}
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Mensagem enviada com sucesso para {numero_destino}")
        return {'sucesso': True, 'response': response.json()}
        
    except Exception as exc:
        logger.error(f"Erro ao enviar mensagem: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)

@shared_task
def processar_mensagem_async(mensagem_id):
    from chatbots.models import Mensagem, Atendimento
    from chatbots.utils import processar_mensagem_handler
    
    lock_key = f'processar_mensagem_{mensagem_id}'
    
    if cache.get(lock_key):
        logger.warning(f"Mensagem {mensagem_id} já está sendo processada")
        return
    
    cache.set(lock_key, True, timeout=300)
    
    try:
        mensagem = Mensagem.objects.select_related('atendimento', 'atendimento__etapa_atual').get(id=mensagem_id)
        
        if mensagem.processada:
            logger.info(f"Mensagem {mensagem_id} já foi processada")
            return
        
        resultado = processar_mensagem_handler(mensagem.atendimento, mensagem)
        
        if resultado and resultado.get('resposta'):
            enviar_mensagem_whatsapp.delay(
                mensagem.atendimento.chatbot_id,
                mensagem.atendimento.numero_whatsapp,
                resultado['resposta'],
                resultado.get('tipo', 'text')
            )
        
        mensagem.processada = True
        mensagem.save()
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem {mensagem_id}: {str(e)}")
        raise
    finally:
        cache.delete(lock_key)

@shared_task
def reativar_clientes_inativos():
    from clientes.models import Cliente
    from chatbots.models import Chatbot, Atendimento
    from metricas.models import MetricaReativacao
    
    dias_inatividade = 30
    data_limite = timezone.now() - timedelta(days=dias_inatividade)
    
    clientes_inativos = Cliente.objects.filter(
        status='ativo',
        ultima_interacao__lt=data_limite
    ).exclude(
        ultima_interacao__isnull=True
    )
    
    chatbot = Chatbot.objects.filter(ativo=True).first()
    
    if not chatbot:
        logger.warning("Nenhum chatbot ativo encontrado para reativação")
        return
    
    mensagem_reativacao = (
        "Olá! Notamos que você não interage conosco há algum tempo. "
        "Temos novidades e ofertas especiais para você! "
        "Gostaria de fazer um novo pedido?"
    )
    
    total_enviados = 0
    
    for cliente in clientes_inativos[:50]:
        try:
            enviar_mensagem_whatsapp.delay(
                chatbot.id,
                cliente.telefone,
                mensagem_reativacao
            )
            
            MetricaReativacao.objects.create(
                chatbot=chatbot,
                cliente=cliente,
                numero_whatsapp=cliente.telefone,
                mensagem_enviada=mensagem_reativacao,
                sucesso=False
            )
            
            total_enviados += 1
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Erro ao reativar cliente {cliente.id}: {str(e)}")
    
    logger.info(f"Total de mensagens de reativação enviadas: {total_enviados}")
    return total_enviados

@shared_task
def limpar_mensagens_antigas():
    from chatbots.models import Mensagem
    from django.db.models import Count
    
    dias_retencao = 90
    data_limite = timezone.now() - timedelta(days=dias_retencao)
    
    mensagens_antigas = Mensagem.objects.filter(
        criada_em__lt=data_limite,
        processada=True
    )
    
    total = mensagens_antigas.count()
    mensagens_antigas.delete()
    
    logger.info(f"Total de mensagens antigas removidas: {total}")
    return total

@shared_task
def verificar_pedidos_pendentes():
    from pedidos.models import Pedido
    from datetime import timedelta
    
    data_limite = timezone.now() - timedelta(hours=24)
    
    pedidos_pendentes = Pedido.objects.filter(
        status='pendente',
        criado_em__lt=data_limite
    )
    
    for pedido in pedidos_pendentes:
        logger.warning(f"Pedido {pedido.id} está pendente há mais de 24 horas")
    
    return pedidos_pendentes.count()
