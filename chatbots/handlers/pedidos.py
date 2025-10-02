from .base import BaseHandler
from pedidos.models import Produto, Pedido
from clientes.models import Cliente
from metricas.models import MetricaPedido, MetricaVenda
from django.utils import timezone

class InicioHandlerPedidos(BaseHandler):
    def handle(self, atendimento, mensagem):
        if not self.validar_tipo_mensagem(mensagem):
            return self.enviar_resposta_invalida()

        categorias = Produto.objects.filter(disponibilidade=True).values_list('categoria', flat=True).distinct()
        
        if not categorias:
            return {
                'resposta': 'Desculpe, não temos produtos disponíveis no momento.',
                'tipo': 'text'
            }

        lista_categorias = '\n'.join([f"{i+1}. {cat}" for i, cat in enumerate(categorias)])
        
        self.salvar_contexto(atendimento, 'categorias_disponiveis', list(categorias))
        self.avancar_etapa(atendimento, 'selecionar_categoria')
        
        return {
            'resposta': f'Olá! Bem-vindo ao nosso sistema de pedidos.\n\nEscolha uma categoria:\n{lista_categorias}\n\nDigite o número da categoria desejada.',
            'tipo': 'text'
        }

class SelecionarCategoriaHandler(BaseHandler):
    def handle(self, atendimento, mensagem):
        if not self.validar_tipo_mensagem(mensagem):
            return self.enviar_resposta_invalida()

        categorias = self.obter_contexto(atendimento, 'categorias_disponiveis', [])
        
        try:
            escolha = int(mensagem.conteudo.strip()) - 1
            if 0 <= escolha < len(categorias):
                categoria_selecionada = categorias[escolha]
                self.salvar_contexto(atendimento, 'categoria_selecionada', categoria_selecionada)
                
                produtos = Produto.objects.filter(categoria=categoria_selecionada, disponibilidade=True)
                lista_produtos = '\n'.join([
                    f"{i+1}. {p.nome} - R$ {p.preco:.2f}" 
                    for i, p in enumerate(produtos)
                ])
                
                self.salvar_contexto(atendimento, 'produtos_disponiveis', [
                    {'id': p.id, 'nome': p.nome, 'preco': float(p.preco)} 
                    for p in produtos
                ])
                
                self.avancar_etapa(atendimento, 'selecionar_produto')
                
                return {
                    'resposta': f'Categoria: {categoria_selecionada}\n\nProdutos disponíveis:\n{lista_produtos}\n\nDigite o número do produto desejado.',
                    'tipo': 'text'
                }
            else:
                return {
                    'resposta': 'Opção inválida. Digite um número da lista.',
                    'tipo': 'text'
                }
        except ValueError:
            return {
                'resposta': 'Por favor, digite apenas o número da categoria.',
                'tipo': 'text'
            }

class SelecionarProdutoHandler(BaseHandler):
    def handle(self, atendimento, mensagem):
        if not self.validar_tipo_mensagem(mensagem):
            return self.enviar_resposta_invalida()

        produtos = self.obter_contexto(atendimento, 'produtos_disponiveis', [])
        
        try:
            escolha = int(mensagem.conteudo.strip()) - 1
            if 0 <= escolha < len(produtos):
                produto = produtos[escolha]
                self.salvar_contexto(atendimento, 'produto_selecionado', produto)
                self.avancar_etapa(atendimento, 'informar_quantidade')
                
                return {
                    'resposta': f'Produto selecionado: {produto["nome"]} - R$ {produto["preco"]:.2f}\n\nQuantos você deseja?',
                    'tipo': 'text'
                }
            else:
                return {
                    'resposta': 'Opção inválida. Digite um número da lista.',
                    'tipo': 'text'
                }
        except ValueError:
            return {
                'resposta': 'Por favor, digite apenas o número do produto.',
                'tipo': 'text'
            }

class InformarQuantidadeHandler(BaseHandler):
    def handle(self, atendimento, mensagem):
        if not self.validar_tipo_mensagem(mensagem):
            return self.enviar_resposta_invalida()

        try:
            quantidade = int(mensagem.conteudo.strip())
            if quantidade <= 0:
                return {
                    'resposta': 'A quantidade deve ser maior que zero.',
                    'tipo': 'text'
                }

            produto = self.obter_contexto(atendimento, 'produto_selecionado')
            
            itens_pedido = self.obter_contexto(atendimento, 'itens_pedido', [])
            itens_pedido.append({
                'produto_id': produto['id'],
                'nome': produto['nome'],
                'preco': produto['preco'],
                'quantidade': quantidade
            })
            self.salvar_contexto(atendimento, 'itens_pedido', itens_pedido)
            
            total = sum(item['preco'] * item['quantidade'] for item in itens_pedido)
            
            self.avancar_etapa(atendimento, 'adicionar_mais')
            
            return {
                'resposta': f'{quantidade}x {produto["nome"]} adicionado!\n\nTotal parcial: R$ {total:.2f}\n\nDeseja adicionar mais produtos?\n1. Sim\n2. Finalizar pedido',
                'tipo': 'text'
            }
        except ValueError:
            return {
                'resposta': 'Por favor, digite apenas a quantidade numérica.',
                'tipo': 'text'
            }

class AdicionarMaisHandler(BaseHandler):
    def handle(self, atendimento, mensagem):
        if not self.validar_tipo_mensagem(mensagem):
            return self.enviar_resposta_invalida()

        resposta = mensagem.conteudo.strip()
        
        if resposta == '1':
            self.avancar_etapa(atendimento, 'inicio_pedidos')
            return {
                'resposta': 'Ok! Vamos adicionar mais produtos.',
                'tipo': 'text'
            }
        elif resposta == '2':
            self.avancar_etapa(atendimento, 'confirmar_pedido')
            
            itens_pedido = self.obter_contexto(atendimento, 'itens_pedido', [])
            resumo = '\n'.join([
                f"{item['quantidade']}x {item['nome']} - R$ {item['preco'] * item['quantidade']:.2f}"
                for item in itens_pedido
            ])
            total = sum(item['preco'] * item['quantidade'] for item in itens_pedido)
            
            return {
                'resposta': f'Resumo do pedido:\n{resumo}\n\nTotal: R$ {total:.2f}\n\nConfirmar pedido?\n1. Sim\n2. Cancelar',
                'tipo': 'text'
            }
        else:
            return {
                'resposta': 'Opção inválida. Digite 1 para adicionar mais ou 2 para finalizar.',
                'tipo': 'text'
            }

class ConfirmarPedidoHandler(BaseHandler):
    def handle(self, atendimento, mensagem):
        if not self.validar_tipo_mensagem(mensagem):
            return self.enviar_resposta_invalida()

        resposta = mensagem.conteudo.strip()
        
        if resposta == '1':
            cliente = atendimento.cliente
            itens_pedido = self.obter_contexto(atendimento, 'itens_pedido', [])
            
            pedido = Pedido.objects.create(
                cliente=cliente,
                itens=[{'produto_id': item['produto_id'], 'quantidade': item['quantidade']} for item in itens_pedido],
                status='pendente'
            )
            pedido.calcular_total()
            
            MetricaPedido.objects.create(
                chatbot=atendimento.chatbot,
                pedido=pedido,
                cliente=cliente,
                valor=pedido.valor_total,
                status='confirmado'
            )
            
            MetricaVenda.objects.create(
                chatbot=atendimento.chatbot,
                pedido=pedido,
                cliente=cliente,
                valor_total=pedido.valor_total
            )
            
            cliente.ultima_interacao = timezone.now()
            cliente.save()
            
            self.finalizar_atendimento(atendimento)
            
            return {
                'resposta': f'Pedido #{pedido.id} confirmado com sucesso!\n\nValor total: R$ {pedido.valor_total:.2f}\n\nObrigado pela preferência!',
                'tipo': 'text'
            }
        elif resposta == '2':
            self.finalizar_atendimento(atendimento)
            return {
                'resposta': 'Pedido cancelado. Até logo!',
                'tipo': 'text'
            }
        else:
            return {
                'resposta': 'Opção inválida. Digite 1 para confirmar ou 2 para cancelar.',
                'tipo': 'text'
            }
