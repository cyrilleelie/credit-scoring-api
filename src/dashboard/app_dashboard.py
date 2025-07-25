# src/dashboard/app_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import requests
from sqlalchemy import text
import warnings
import tempfile
import os
from datetime import datetime, time
import sys

# --- Bloc d'initialisation du chemin ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.config import settings
from src.database.database import engine
from src.database import models
from src.api.security import verify_password
from sqlalchemy.orm import sessionmaker

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

# --- TEST DE CONNEXION DIRECTE A LA BDD ---
def direct_db_login(username, password):
    """
    Fonction de débogage : se connecte directement à la BDD pour vérifier les identifiants.
    """
    st.info("--- DÉBUT DU TEST DE CONNEXION DIRECTE À LA BDD ---")
    db_engine = None
    try:
        db_engine = engine
        st.success("1. Moteur SQLAlchemy créé avec succès.")
        
        SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        db = SessionTest()
        st.success("2. Session de base de données ouverte.")

        user = db.query(models.User).filter(models.User.username == username).first()
        db.close()
        st.success("3. Requête utilisateur exécutée et session fermée.")

        if user:
            st.success(f"4. Utilisateur '{username}' trouvé dans la base de données.")
            if verify_password(password, user.hashed_password):
                st.success("5. Le mot de passe est CORRECT. Les secrets sont VALIDES !")
                st.balloons()
            else:
                st.error("6. Le mot de passe est INCORRECT.")
        else:
            st.error(f"6. Utilisateur '{username}' NON TROUVÉ dans la base de données.")

    except Exception as e:
        st.error(f"--- ERREUR CRITIQUE LORS DE LA CONNEXION À LA BDD ---")
        st.exception(e)
    finally:
        st.info("--- FIN DU TEST DE CONNEXION ---")

# --- Interface Principale ---
st.set_page_config(layout="wide", page_title="Dashboard de Scoring Crédit")

st.title("Connexion au Dashboard - Mode Débogage BDD")
with st.form("login_form"):
    username = st.text_input("Nom d'utilisateur", value=settings.api_user or "")
    password = st.text_input("Mot de passe", type="password")
    submitted = st.form_submit_button("Lancer le test de connexion")
    if submitted:
        direct_db_login(username, password)

