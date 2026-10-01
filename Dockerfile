FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema (gcc para compilar gevent, etc)
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     python3-dev     && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn gevent

# Copiar o código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/uploads /app/static

# Expor a porta do Gunicorn
EXPOSE 8000

# Rodar com Gunicorn (gevent worker é OBRIGATÓRIO para Flask-SocketIO)
CMD ["gunicorn", "--worker-class", "gevent", "--workers", "2", "--bind", "0.0.0.0:8000", "app:app"]
