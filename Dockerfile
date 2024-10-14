# Imagem oficial do Python como base
FROM python:3.12-slim

# Não criar um ambiente (foi opção de projeto)
ENV POETRY_VIRTUALENVS_CREATE=false

# Diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos da pasta local para o diretório no container
COPY . /app

# Instala as dependências necessárias
RUN pip install poetry
# Instalações do Poetry correndo em paralelo
RUN poetry config installer.max-workers 10
# Configurações do Poetry para instalar sem perguntas
RUN poetry install --no-interaction --no-ansi

# Porta padrão Docker para conexão
EXPOSE 8000

# Comando para rodar o aplicativo
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "madr.app:app"]
