#!/bin/bash

# Démarre le serveur de l'API FastAPI en arrière-plan
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Démarre le dashboard Streamlit au premier plan
# C'est ce processus qui maintiendra le conteneur en vie
streamlit run app.py --server.port 7860 --server.address 0.0.0.0
