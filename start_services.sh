
#!/bin/bash

echo "=== Limpando processos antigos ==="
pkill -f redis-server 2>/dev/null || true
pkill -f celery 2>/dev/null || true
rm -f /tmp/redis.log /tmp/celery.pid 2>/dev/null || true

echo ""
echo "=== Iniciando Redis em background ==="
nohup redis-server --port 6379 --bind 127.0.0.1 --protected-mode no --loglevel verbose > /tmp/redis.log 2>&1 &
REDIS_PID=$!

echo "Redis iniciado com PID: $REDIS_PID"
echo "Aguardando Redis ficar pronto..."

# Tenta conectar por até 15 segundos
for i in {1..15}; do
    if redis-cli -p 6379 ping > /dev/null 2>&1; then
        echo "✓ Redis está rodando e respondendo!"
        break
    fi
    echo "Tentativa $i/15..."
    sleep 1
done

# Verifica se Redis está realmente funcionando
if ! redis-cli -p 6379 ping > /dev/null 2>&1; then
    echo "✗ ERRO: Redis falhou ao iniciar"
    echo "Log do Redis:"
    cat /tmp/redis.log
    exit 1
fi

echo ""
echo "=== Iniciando Celery Worker ==="
celery -A config worker -l info --detach --logfile=/tmp/celery.log --pidfile=/tmp/celery.pid

echo "Aguardando Celery iniciar..."
sleep 3

if [ -f /tmp/celery.pid ]; then
    echo "✓ Celery worker iniciado com sucesso"
else
    echo "⚠ Aviso: Celery pode não ter iniciado corretamente"
fi

echo ""
echo "=== Iniciando Django ==="
python manage.py runserver 0.0.0.0:5000
