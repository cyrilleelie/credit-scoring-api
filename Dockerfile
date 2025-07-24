# Utilise une image de base Python 3.12 slim
FROM python:3.12-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Installe la dépendance système requise par LightGBM
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

# Copie les fichiers de configuration de Poetry
COPY pyproject.toml poetry.lock ./

# Installe Poetry et les dépendances du projet
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --only main

# Copie tout le code de l'application
COPY . .

# Expose les ports nécessaires
EXPOSE 8501
EXPOSE 7860

# --- COMMANDE DE DÉMARRAGE MODIFIÉE ---
# Lance UNIQUEMENT le dashboard Streamlit pour le débogage.
# On utilise la forme "exec" pour plus de robustesse.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
