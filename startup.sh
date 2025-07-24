#!/bin/bash

# Active le mode "exit on error"
set -e

echo "--- [DEBUG] Lancement du serveur API FastAPI en PREMIER PLAN pour le débogage ---"

# Lance l'API en premier plan pour voir tous ses logs, y compris les erreurs fatales.
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
