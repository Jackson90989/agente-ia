FROM python:3.10-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de dependências
COPY requirements.txt ./

# Instala dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante do código
COPY . .


# Define variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV PORT=10000
ENV PYTHONPATH=/app

# Comando para rodar o Gunicorn apontando para o wsgi.py
CMD ["gunicorn", "--bind", ":10000", "wsgi:app"]