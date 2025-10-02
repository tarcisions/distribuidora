from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
import logging
import json
import hmac
import hashlib

from .models import Chatbot, Mensagem
from .utils import obter_ou_criar_atendimento, validar_tipo_mensagem_media
from metricas.models import MetricaContato
from tarefas.tasks import processar_mensagem_async

logger = logging.getLogger(__name__)

def verificar_assinatura_webhook(payload_body, signature_header, app_secret):
    try:
        expected_signature = hmac.new(
            app_secret.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        if signature_header.startswith('sha256='):
            signature_header = signature_header[7:]
        
        return hmac.compare_digest(expected_signature, signature_header)
    except Exception as e:
        logger.error(f'Erro ao verificar assinatura: {str(e)}')
        return False

@csrf_exempt
@api_view(['GET', 'POST'])
def webhook_whatsapp(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if not challenge:
            logger.warning('Challenge ausente na verificação do webhook')
            return Response({'error': 'Missing challenge parameter'}, status=status.HTTP_400_BAD_REQUEST)
        
        if mode == 'subscribe':
            chatbot = Chatbot.objects.filter(verify_token=token, ativo=True).first()
            
            if chatbot:
                logger.info(f'Webhook verificado com sucesso para chatbot: {chatbot.nome}')
                return HttpResponse(challenge, content_type='text/plain')
            else:
                logger.warning(f'Token de verificação inválido: {token}')
                return Response({'error': 'Invalid verify token'}, status=status.HTTP_403_FORBIDDEN)
        else:
            logger.warning('Modo de verificação inválido')
            return Response({'error': 'Invalid mode'}, status=status.HTTP_403_FORBIDDEN)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if not data.get('entry'):
                return Response(status=status.HTTP_200_OK)
            
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    if change.get('field') != 'messages':
                        continue
                    
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    metadata = value.get('metadata', {})
                    
                    phone_number_id = metadata.get('phone_number_id')
                    
                    chatbot = Chatbot.objects.filter(
                        meta_phone_number_id=phone_number_id,
                        ativo=True
                    ).first()
                    
                    if not chatbot:
                        logger.warning(f'Chatbot não encontrado para phone_number_id: {phone_number_id}')
                        continue
                    
                    signature = request.headers.get('X-Hub-Signature-256', '')
                    
                    if chatbot.meta_app_secret and signature:
                        if not verificar_assinatura_webhook(request.body, signature, chatbot.meta_app_secret):
                            logger.warning(f'Assinatura inválida para chatbot: {chatbot.nome}')
                            return Response(status=status.HTTP_403_FORBIDDEN)
                    elif chatbot.meta_app_secret:
                        logger.warning(f'Webhook sem assinatura para chatbot: {chatbot.nome}')
                        return Response(status=status.HTTP_403_FORBIDDEN)
                    
                    for msg in messages:
                        processar_mensagem_recebida(chatbot, msg)
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'Erro ao processar webhook: {str(e)}')
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def processar_mensagem_recebida(chatbot, msg_data):
    try:
        meta_message_id = msg_data.get('id')
        numero_whatsapp = msg_data.get('from')
        msg_type = msg_data.get('type', 'unknown')
        
        if Mensagem.objects.filter(meta_message_id=meta_message_id).exists():
            logger.info(f'Mensagem duplicada ignorada: {meta_message_id}')
            return
        
        atendimento = obter_ou_criar_atendimento(chatbot, numero_whatsapp)
        
        MetricaContato.objects.create(
            chatbot=chatbot,
            cliente=atendimento.cliente,
            numero_whatsapp=numero_whatsapp,
            tipo_interacao='mensagem_recebida',
            detalhes={'tipo_mensagem': msg_type}
        )
        
        conteudo = ''
        
        if msg_type == 'text':
            conteudo = msg_data.get('text', {}).get('body', '')
        elif msg_type == 'interactive':
            interactive_data = msg_data.get('interactive', {})
            if interactive_data.get('type') == 'button_reply':
                conteudo = interactive_data.get('button_reply', {}).get('title', '')
            elif interactive_data.get('type') == 'list_reply':
                conteudo = interactive_data.get('list_reply', {}).get('title', '')
        
        mensagem = Mensagem.objects.create(
            atendimento=atendimento,
            meta_message_id=meta_message_id,
            direcao='recebida',
            tipo=msg_type,
            conteudo=conteudo,
            payload_completo=msg_data,
            processada=False
        )
        
        if validar_tipo_mensagem_media(msg_type):
            from tarefas.tasks import enviar_mensagem_whatsapp
            
            enviar_mensagem_whatsapp.delay(
                chatbot.id,
                numero_whatsapp,
                'Entrada inválida. Por favor, envie apenas texto ou use as opções do menu.',
                'text'
            )
            
            mensagem.processada = True
            mensagem.save()
            
            logger.info(f'Mensagem de mídia bloqueada: {msg_type}')
        else:
            processar_mensagem_async.delay(mensagem.id)
        
        if atendimento.cliente:
            atendimento.cliente.ultima_interacao = timezone.now()
            atendimento.cliente.save()
        
    except Exception as e:
        logger.error(f'Erro ao processar mensagem recebida: {str(e)}')
