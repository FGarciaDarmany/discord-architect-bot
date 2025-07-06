# Usa Python 3.11 oficial
FROM python:3.11

WORKDIR /app

# Copia dependencias e instala
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia todo el proyecto
COPY . .

# Ejecuta tu bot
CMD ["python", "bot.py"]
