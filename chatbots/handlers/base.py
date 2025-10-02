from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseHandler(ABC):
    @abstractmethod
    def handle(self, atendimento, mensagem) -> Dict[str, Any]:
        pass

    def validar_tipo_mensagem(self, mensagem) -> bool:
        return mensagem.tipo in ['text', 'interactive']

    def enviar_resposta_invalida(self) -> Dict[str, Any]:
        return {
            'resposta': 'Entrada inválida. Por favor, envie apenas texto ou use as opções do menu.',
            'tipo': 'text'
        }

    def salvar_contexto(self, atendimento, chave: str, valor: Any):
        atendimento.contexto[chave] = valor
        atendimento.save()

    def obter_contexto(self, atendimento, chave: str, padrao: Any = None) -> Any:
        return atendimento.contexto.get(chave, padrao)

    def avancar_etapa(self, atendimento, proxima_etapa_codigo: str):
        from chatbots.models import Etapa
        proxima_etapa = Etapa.objects.filter(
            chatbot=atendimento.chatbot,
            codigo=proxima_etapa_codigo,
            ativa=True
        ).first()
        
        if proxima_etapa:
            atendimento.etapa_atual = proxima_etapa
            atendimento.save()
            return True
        return False

    def finalizar_atendimento(self, atendimento):
        from django.utils import timezone
        atendimento.status = 'finalizado'
        atendimento.finalizado_em = timezone.now()
        atendimento.save()
