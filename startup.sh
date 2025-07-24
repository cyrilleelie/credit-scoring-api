#!/bin/bash

echo "--- [DEBUG] Vérification des variables d'environnement ---"
printenv | grep -E 'API_URL|DB_HOST|MODEL_PATH'

# --- NOUVEAU BLOC DE DÉBOGAGE ---
echo "--- [DEBUG] Tentative d'importation de l'application API pour détection d'erreur ---"
python -c "from src.api.main import app"
IMPORT_STATUS=$? # Récupère le code de sortie de la commande précédente

if [ $IMPORT_STATUS -ne 0 ]; then
    echo "--- ERREUR CRITIQUE : L'importation de l'application API a échoué. Le démarrage est annulé. ---"
    exit 1
else
    echo "--- SUCCÈS : L'importation de l'application API a réussi. ---"
fi
# --- FIN DU NOUVEAU BLOC ---


echo "--- Démarrage du serveur API FastAPI en arrière-plan ---"
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

sleep 5

echo "--- Contenu des logs de l'API (api.log) ---"
cat api.log
echo "--------------------------------------------"


echo "--- Démarrage du Dashboard Streamlit ---"
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
