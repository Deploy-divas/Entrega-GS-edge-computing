FROM ubuntu:latest
LABEL authors="laura"

ENTRYPOINT ["top", "-b"]

# Define a versão do Python
FROM python:3.10-slim

# Define a pasta de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências e instala as bibliotecas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código para dentro do contêiner
COPY . .

# Expõe a porta que a API vai utilizar
EXPOSE 8000

# Comando para iniciar o servidor (Exemplo usando FastAPI)
CMD ["fastapi", "main:app", "--host", "0.0.0.0", "--port", "8000"]