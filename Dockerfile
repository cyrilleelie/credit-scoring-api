# Utilise une image Python 3.12 légère
FROM python:3.12-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Installe les dépendances système requises (pour LightGBM et pour notre script de test)
RUN apt-get update && apt-get install -y libgomp1 curl

# Crée un utilisateur non-privilégié pour des raisons de sécurité
RUN useradd -m -u 1000 appuser
USER appuser

# Copie les fichiers de configuration de Poetry
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./

# Installe les dépendances Python avec Poetry
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --only main

# Copie tout le reste du code de l'application
COPY --chown=appuser:appuser . .

# Rend le script de démarrage exécutable
RUN chmod +x startup.sh

# Commande pour lancer l'application
CMD ["./startup.sh"]
