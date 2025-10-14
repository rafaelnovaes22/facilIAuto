# 🔧 Operations Manager: Dockerfile para produção
# Multi-stage build para otimização de tamanho

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Labels para metadata
LABEL maintainer="FacilIAuto Team"
LABEL version="1.0.0"
LABEL description="FacilIAuto Backend API - Multi-tenant Car Recommendation System"

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 faciliauto && \
    mkdir -p /app /app/data /app/logs && \
    chown -R faciliauto:faciliauto /app

# Workdir
WORKDIR /app

# Copiar dependências do builder
COPY --from=builder /root/.local /home/faciliauto/.local

# Copiar código
COPY --chown=faciliauto:faciliauto . .

# Configurar PATH
ENV PATH=/home/faciliauto/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Usar usuário não-root
USER faciliauto

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Expor porta
EXPOSE 8000

# Comando para rodar
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

