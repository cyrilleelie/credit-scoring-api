#!/bin/bash

echo "--- [DEBUG] Vérification des variables d'environnement ---"
# Affiche quelques variables clés pour s'assurer qu'elles sont bien chargées depuis les secrets
printenv | grep -E 'API_URL|DB_HOST|MODEL_PATH'

echo "--- Démarrage du serveur API FastAPI en arrière-plan ---"

# Lance l'API et redirige ses logs vers un fichier
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

# Attend quelques secondes
echo "--- Attente de 5 secondes... ---"
sleep 5

echo "--- Contenu des logs de l'API (api.log) ---"
# Affiche le contenu du log, même s'il est vide
cat api.log
echo "--------------------------------------------"

echo "--- [DEBUG] Vérification du processus API ---"
# Vérifie si un processus écoute bien sur le port 8000 avec netstat
if netstat -tln | grep -q 8000; then
    echo "SUCCÈS : Un processus API écoute bien sur le port 8000."
else
    echo "ERREUR : Aucun processus API ne semble tourner. L'API a probablement planté au démarrage."
fi

echo "--- Démarrage du Dashboard Streamlit ---"
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
