
# Sistema de Chatbots WhatsApp Corporativo

Sistema Django completo para gerenciamento de múltiplos chatbots WhatsApp corporativos com processamento assíncrono, handlers modulares e integração com Meta WhatsApp Business API.

## 🚀 Funcionalidades

- ✅ **Múltiplos Chatbots**: Gerencie vários chatbots simultaneamente
- ✅ **Handlers Modulares**: Sistema extensível de handlers por fluxo
- ✅ **Processamento Assíncrono**: Celery + Redis para alta performance
- ✅ **Webhook Seguro**: Validação HMAC SHA256 das mensagens
- ✅ **Sistema de Métricas**: Acompanhamento detalhado de interações
- ✅ **Reativação Automática**: Campanha para clientes inativos
- ✅ **API REST Completa**: Endpoints para integração

## 📋 Pré-requisitos

### Ambiente Local

- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- Ngrok (para testes com webhook local)

### Produção (Replit/Render/VPS)

- Mesmos requisitos acima
- Mínimo 512MB RAM (recomendado 1GB+)
- 1 CPU core (recomendado 2+)

## 🔧 Instalação Local

### 1. Clone e Configure o Ambiente

```bash
# Clone o projeto
git clone <seu-repositorio>
cd chatbot_whatsapp

# Instale as dependências
pip install -r requirements.txt

# Ou com uv (mais rápido)
pip install uv
uv pip install -r requirements.txt
```

### 2. Configure o Banco de Dados PostgreSQL

```bash
# Acesse o PostgreSQL
sudo -u postgres psql

# Crie o banco
CREATE DATABASE chatbot_db;
CREATE USER chatbot_user WITH PASSWORD 'senha_segura';
ALTER ROLE chatbot_user SET client_encoding TO 'utf8';
ALTER ROLE chatbot_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE chatbot_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;
\q
```

### 3. Configure Redis

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# macOS
brew install redis
brew services start redis

# Teste a conexão
redis-cli ping
# Deve retornar: PONG
```

### 4. Configure as Variáveis de Ambiente

Crie o arquivo `.env`:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
DEBUG=True
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
DATABASE_URL=postgresql://chatbot_user:senha_segura@localhost:5432/chatbot_db
REDIS_URL=redis://127.0.0.1:6379/0

# WhatsApp - Obtenha em developers.facebook.com
WHATSAPP_VERIFY_TOKEN=token_verificacao_webhook
WHATSAPP_APP_SECRET=seu_app_secret_meta

# PostgreSQL (alternativo)
PGDATABASE=chatbot_db
PGUSER=chatbot_user
PGPASSWORD=senha_segura
PGHOST=localhost
PGPORT=5432
```

### 5. Execute as Migrações

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Inicie os Serviços

**Terminal 1 - Django:**
```bash
python manage.py runserver 0.0.0.0:5000
```

**Terminal 2 - Celery Worker:**
```bash
celery -A config worker -l info
```

**Terminal 3 - Celery Beat (tarefas agendadas):**
```bash
celery -A config beat -l info
```

**Terminal 4 - Ngrok (webhook público):**
```bash
ngrok http 5000
```

### 7. Configure o Webhook no Meta

1. Acesse https://developers.facebook.com
2. Vá em seu App WhatsApp > Configuração > Webhooks
3. Cole a URL do ngrok: `https://seu-ngrok.ngrok.io/api/chatbots/webhook/`
4. Token de verificação: use o mesmo do `.env` (`WHATSAPP_VERIFY_TOKEN`)
5. Inscreva-se em `messages`

## 🌐 Deploy no Replit

### 1. Importe o Projeto

1. Acesse https://replit.com
2. Clique em "Create Repl" > "Import from GitHub"
3. Cole a URL do repositório

### 2. Configure os Secrets

No painel lateral, acesse **Secrets** e adicione:

```
SECRET_KEY=sua-chave-secreta
WHATSAPP_VERIFY_TOKEN=token_verificacao
WHATSAPP_APP_SECRET=seu_app_secret_meta
```

### 3. Execute

Clique no botão **Run**. O script `start_services.sh` irá:
- Iniciar Redis automaticamente
- Iniciar Celery Worker
- Iniciar Django na porta 5000

### 4. Configure o Webhook

Use a URL pública do Replit:
```
https://seu-projeto.replit.app/api/chatbots/webhook/
```

## 🚀 Deploy no Render

### 1. Crie os Serviços

**a) PostgreSQL:**
- New > PostgreSQL
- Copie a `Internal Database URL`

**b) Redis:**
- New > Redis
- Copie a `Internal Redis URL`

**c) Web Service (Django):**
- New > Web Service
- Conecte seu repositório GitHub

### 2. Configure o Web Service

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

**Start Command:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

**Environment Variables:**
```
DEBUG=False
SECRET_KEY=sua-chave-secreta
DATABASE_URL=<cole a Internal Database URL>
REDIS_URL=<cole a Internal Redis URL>
WHATSAPP_VERIFY_TOKEN=token_verificacao
WHATSAPP_APP_SECRET=seu_app_secret_meta
PYTHON_VERSION=3.11.0
```

### 3. Crie o Background Worker (Celery)

**New > Background Worker:**

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
celery -A config worker -l info
```

**Environment Variables:** (mesmas do Web Service)

### 4. Crie o Celery Beat

**New > Background Worker:**

**Start Command:**
```bash
celery -A config beat -l info
```

**Environment Variables:** (mesmas do Web Service)

### 5. Configure o Webhook

URL pública do Render:
```
https://seu-projeto.onrender.com/api/chatbots/webhook/
```

## ☁️ Deploy em VPS (AWS/DigitalOcean/Linode)

### Especificações Mínimas

- **RAM:** 1GB (2GB recomendado)
- **CPU:** 1 core (2 cores recomendado)
- **Disco:** 20GB SSD
- **OS:** Ubuntu 22.04 LTS

### 1. Prepare o Servidor

```bash
# Atualize o sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instale dependências
sudo apt-get install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib redis-server nginx supervisor
```

### 2. Configure PostgreSQL e Redis

```bash
# PostgreSQL
sudo -u postgres psql
CREATE DATABASE chatbot_db;
CREATE USER chatbot_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;
\q

# Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### 3. Deploy da Aplicação

```bash
# Clone o projeto
cd /var/www
sudo git clone <seu-repo> chatbot
cd chatbot

# Crie o ambiente virtual
sudo python3.11 -m venv venv
sudo chown -R $USER:$USER venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
pip install gunicorn

# Configure .env
sudo nano .env
# Cole as configurações de produção

# Execute migrações
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4. Configure Gunicorn com Supervisor

Crie `/etc/supervisor/conf.d/chatbot.conf`:

```ini
[program:chatbot_django]
command=/var/www/chatbot/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
directory=/var/www/chatbot
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/chatbot/django.log
stderr_logfile=/var/log/chatbot/django_error.log

[program:chatbot_celery]
command=/var/www/chatbot/venv/bin/celery -A config worker -l info
directory=/var/www/chatbot
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/chatbot/celery.log
stderr_logfile=/var/log/chatbot/celery_error.log

[program:chatbot_beat]
command=/var/www/chatbot/venv/bin/celery -A config beat -l info
directory=/var/www/chatbot
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/chatbot/beat.log
stderr_logfile=/var/log/chatbot/beat_error.log
```

```bash
# Crie diretório de logs
sudo mkdir -p /var/log/chatbot
sudo chown www-data:www-data /var/log/chatbot

# Ative os serviços
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### 5. Configure Nginx

Crie `/etc/nginx/sites-available/chatbot`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/chatbot/staticfiles/;
    }
}
```

```bash
# Ative o site
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Configure SSL (HTTPS) com Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

### 7. Configure o Webhook

URL final com HTTPS:
```
https://seu-dominio.com/api/chatbots/webhook/
```

## 📡 API REST

### Endpoints Disponíveis

**Webhook:**
- `GET/POST /api/chatbots/webhook/` - Webhook WhatsApp

**Clientes:**
- `GET /api/clientes/` - Lista clientes
- `POST /api/clientes/` - Cria cliente
- `GET /api/clientes/{id}/` - Detalhes do cliente
- `PUT /api/clientes/{id}/` - Atualiza cliente
- `DELETE /api/clientes/{id}/` - Remove cliente

**Produtos:**
- `GET /api/pedidos/produtos/` - Lista produtos
- `POST /api/pedidos/produtos/` - Cria produto

**Pedidos:**
- `GET /api/pedidos/pedidos/` - Lista pedidos
- `POST /api/pedidos/pedidos/` - Cria pedido

## 🔐 Configuração do Chatbot

### 1. Acesse o Admin

```
http://localhost:5000/admin/
```

### 2. Crie um Chatbot

- Nome: `Chatbot Principal`
- Número: `5511999999999`
- Meta Phone Number ID: (obtenha no Meta Business)
- Meta Business Account ID: (obtenha no Meta Business)
- Meta Access Token: (obtenha no Meta Business)
- Meta App Secret: (obtenha no Meta Business)
- Verify Token: (mesmo do `.env`)
- Ativo: ✓

### 3. Configure as Etapas

Crie as etapas do fluxo de pedidos:

| Código | Handler Path | Ordem |
|--------|--------------|-------|
| `inicio` | `chatbots.handlers.pedidos.InicioHandlerPedidos` | 1 |
| `selecionar_categoria` | `chatbots.handlers.pedidos.SelecionarCategoriaHandler` | 2 |
| `selecionar_produto` | `chatbots.handlers.pedidos.SelecionarProdutoHandler` | 3 |
| `informar_quantidade` | `chatbots.handlers.pedidos.InformarQuantidadeHandler` | 4 |
| `adicionar_mais` | `chatbots.handlers.pedidos.AdicionarMaisHandler` | 5 |
| `confirmar_pedido` | `chatbots.handlers.pedidos.ConfirmarPedidoHandler` | 6 |

## 📊 Monitoramento

### Logs em Produção

```bash
# Django
sudo tail -f /var/log/chatbot/django.log

# Celery Worker
sudo tail -f /var/log/chatbot/celery.log

# Celery Beat
sudo tail -f /var/log/chatbot/beat.log

# Nginx
sudo tail -f /var/log/nginx/access.log
```

### Status dos Serviços

```bash
sudo supervisorctl status
```

### Reiniciar Serviços

```bash
# Todos
sudo supervisorctl restart all

# Individual
sudo supervisorctl restart chatbot_django
sudo supervisorctl restart chatbot_celery
sudo supervisorctl restart chatbot_beat
```

## 🛠️ Tarefas Agendadas

O sistema já vem com tarefas configuradas via Celery Beat:

- **Reativação de Clientes**: Diariamente às 10h
- **Limpeza de Mensagens**: Semanalmente às 2h
- **Verificação de Pedidos**: A cada 6 horas

Configure no Django Admin em **Periodic Tasks**.

## 🔄 Backup e Restore

### Backup PostgreSQL

```bash
pg_dump chatbot_db > backup_$(date +%Y%m%d).sql
```

### Restore PostgreSQL

```bash
psql chatbot_db < backup_20250102.sql
```

## 🐛 Troubleshooting

### Redis não conecta

```bash
# Verifique se está rodando
redis-cli ping

# Reinicie
sudo systemctl restart redis
```

### Celery não processa mensagens

```bash
# Verifique conexão Redis
redis-cli -h localhost -p 6379 ping

# Reinicie worker
sudo supervisorctl restart chatbot_celery
```

### Webhook não recebe mensagens

1. Verifique HTTPS (obrigatório)
2. Confirme token de verificação
3. Valide assinatura HMAC
4. Veja logs do Django

## 📝 Licença

Projeto proprietário - Todos os direitos reservados

## 📞 Suporte

Para dúvidas e suporte, entre em contato com a equipe de desenvolvimento.
