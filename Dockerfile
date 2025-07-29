# Utilise une image Python 3.12 légère
FROM python:3.12-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Installe les dépendances système requises
RUN apt-get update && apt-get install -y libgomp1 curl

# Copie les fichiers de configuration de Poetry
COPY pyproject.toml poetry.lock ./

# Installe les dépendances Python avec les droits root
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry \
    && python -m poetry config virtualenvs.create false \
    && python -m poetry install --no-root --only main

# Copie tout le reste du code de l'application
COPY . .

# Crée l'utilisateur non-privilégié
RUN useradd -m -u 1000 appuser

# Change le propriétaire de tous les fichiers pour le nouvel utilisateur
RUN chown -R appuser:appuser /app

# Bascule vers l'utilisateur non-privilégié pour l'exécution
USER appuser

# Rend le script de démarrage exécutable
RUN chmod +x startup.sh

# Commande pour lancer l'application
CMD ["./startup.sh"]
