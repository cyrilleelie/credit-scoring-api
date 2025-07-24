#!/bin/bash

echo "--- Démarrage du serveur API FastAPI en arrière-plan ---"

# Lance l'API, redirige ses logs et capture son Process ID (PID)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
API_PID=$!

echo "API lancée avec le PID: $API_PID. Attente de 8 secondes pour la stabilisation..."
sleep 8

# Vérifie si le processus de l'API est toujours en cours d'exécution
if kill -0 $API_PID > /dev/null 2>&1; then
    echo "--- SUCCÈS: Le processus de l'API est toujours actif. ---"
else
    echo "--- ERREUR CRITIQUE: Le processus de l'API a planté au démarrage. ---"
    echo "--- Affichage des logs de l'API (api.log) pour le débogage : ---"
    cat api.log
    echo "---------------------------------------------------------"
    exit 1 # Arrête le script pour que l'erreur soit visible dans les logs HF
fi

echo "--- Démarrage du Dashboard Streamlit ---"
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
