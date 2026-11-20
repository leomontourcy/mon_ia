FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

WORKDIR /app

# Dépendances système : FFmpeg (rendu vidéo), libs OpenCV, police pour l'écran titre
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Utilisateur non-root
RUN useradd --create-home appuser \
    && mkdir -p uploads outputs instance \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

# Un seul worker : la progression des montages est gardée en mémoire et Socket.IO
# a besoin que toutes les requêtes d'un client arrivent sur le même processus.
# Les threads permettent de servir plusieurs utilisateurs en parallèle.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--worker-class", "gthread", "--workers", "1", "--threads", "16", "--timeout", "300", "app:app"]
