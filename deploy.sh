#!/bin/bash
echo "🚀 Iniciando deploy do ThinkinOS v2.0..."

# Parar containers antigos
docker-compose down

# Construir a imagem atualizada
echo "🔨 Construindo imagens Docker..."
docker-compose build --no-cache

# Subir os serviços
echo "🟢 Iniciando serviços (App + Nginx)..."
docker-compose up -d

echo "✅ Deploy concluído! Verifique com: docker-compose ps"
echo "📝 Logs da aplicação: docker-compose logs -f app"
