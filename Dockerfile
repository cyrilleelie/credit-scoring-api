# 1. Utiliser une image Python de base
FROM python:3.12-slim

# 2. Mettre à jour les paquets et installer les dépendances système requises
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# 3. Définir le répertoire de travail
WORKDIR /app

# 4. Créer un utilisateur non-privilégié pour la sécurité
RUN useradd -m -u 1000 appuser

# 5. Copier les fichiers de configuration et installer les dépendances en tant que root
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry \
    && python -m poetry config virtualenvs.create false \
    && python -m poetry install --no-root --only main

# 6. Copier le reste du code de l'application
COPY . .
# S'assurer que le nouvel utilisateur est propriétaire des fichiers
RUN chown -R appuser:appuser /app

# 7. Changer d'utilisateur pour l'exécution
USER appuser

# 8. Exposer le port de l'API
EXPOSE 8000

# 9. Commande pour lancer le serveur API
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
