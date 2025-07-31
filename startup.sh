#!/bin/bash

# Lance le serveur API FastAPI en arrière-plan et redirige sa sortie (stdout & stderr) vers un fichier
echo "--- Démarrage du serveur API FastAPI en arrière-plan ---"
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &> api.log &

# Lance un processus en arrière-plan pour afficher en continu les logs de l'API
echo "--- Streaming des logs de l'API en arrière-plan ---"
tail -f api.log &

# Lance le Dashboard Streamlit en premier plan (ce sont ses logs que nous verrons principalement)
echo "--- Démarrage du Dashboard Streamlit en premier plan ---"
streamlit run app.py --server.port=7860 --server.address=0.0.0.0
