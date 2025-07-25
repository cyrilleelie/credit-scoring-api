#!/bin/bash

# Active le mode "exit on error" pour arrêter le script si une commande échoue.
set -e

echo "--- Démarrage du serveur API FastAPI en arrière-plan ---"
# Lance l'API et redirige sa sortie (standard et erreur) vers un fichier de log.
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

echo "--- Streaming des logs de l'API en arrière-plan ---"
# Lance un processus en arrière-plan qui affiche en continu le contenu du fichier
# de log de l'API. Cela nous permettra de voir les erreurs en temps réel.
tail -f api.log &

echo "--- Démarrage du Dashboard Streamlit en premier plan ---"
# Lance le dashboard. Ce processus reste en premier plan.
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
