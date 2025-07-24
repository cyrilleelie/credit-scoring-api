#!/bin/bash

echo "--- Démarrage du serveur API FastAPI en arrière-plan ---"
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

echo "--- Attente de 8 secondes pour la stabilisation de l'API... ---"
sleep 8

echo "--- [DEBUG] Vérification de la santé de l'API avec curl ---"
# On envoie une requête à l'endpoint racine de l'API
curl --fail http://localhost:8000/

# On récupère le code de sortie de la commande curl
# 0 signifie succès, tout autre code signifie échec
STATUS=$?

if [ $STATUS -eq 0 ]; then
    echo "--- SUCCÈS : Le serveur API répond correctement. ---"
else
    echo "--- ERREUR CRITIQUE: Le serveur API ne répond pas. Il a probablement planté. ---"
    echo "--- Affichage des logs de l'API (api.log) pour le débogage : ---"
    cat api.log
    echo "---------------------------------------------------------"
    exit 1 # Arrête le script pour que l'erreur soit visible
fi

echo "--- Démarrage du Dashboard Streamlit ---"
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
