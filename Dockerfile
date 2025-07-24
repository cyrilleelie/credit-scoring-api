# Utilise une image de base Python 3.12 slim
FROM python:3.12-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Installe les dépendances système requises (pour LightGBM et Git LFS)
RUN apt-get update && apt-get install -y libgomp1 git-lfs && rm -rf /var/lib/apt/lists/*

# Crée un utilisateur non-privilégié pour exécuter l'application
RUN useradd -ms /bin/bash appuser

# Copie les fichiers de configuration de Poetry
COPY pyproject.toml poetry.lock ./

# Installe Poetry et les dépendances du projet
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --only main

# --- CORRECTION APPLIQUÉE ICI ---
# Copie tout le code de l'application AVANT de changer les permissions
COPY . .

# Rend le script de démarrage exécutable
RUN chmod +x startup.sh
# ---------------------------------

# Change le propriétaire de tous les fichiers de l'application
RUN chown -R appuser:appuser /app

# Passe à l'utilisateur non-privilégié
USER appuser

# Expose les ports pour l'API et le dashboard
EXPOSE 8000 7860

# Commande finale pour lancer l'application
CMD ["./startup.sh"]
