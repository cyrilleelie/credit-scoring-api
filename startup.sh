#!/bin/bash

# Affiche un message pour indiquer le début du démarrage de l'API
echo "--- Démarrage du serveur API FastAPI en arrière-plan ---"

# Démarre le serveur de l'API et redirige TOUTE sa sortie (standard et erreur) vers un fichier api.log
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

# Attend quelques secondes pour laisser le temps à l'API de démarrer ou de planter
echo "--- Attente de 5 secondes pour la stabilisation de l'API... ---"
sleep 5

# Affiche le contenu du fichier de log de l'API pour le débogage
echo "--- Contenu des logs de démarrage de l'API (api.log) ---"
cat api.log
echo "--------------------------------------------------------"


# Affiche un message pour indiquer le début du démarrage du dashboard
echo "--- Démarrage du Dashboard Streamlit ---"

# Démarre le dashboard Streamlit au premier plan
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
