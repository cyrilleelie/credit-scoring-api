# src/dashboard/app_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import requests
import warnings
import json
from datetime import datetime, time
import os
import sys

# --- Bloc d'initialisation du chemin ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.config import settings

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

# --- Fonctions d'API ---

@st.cache_data(ttl=60)
def get_client_ids():
    """Récupère la liste des ID clients depuis l'API."""
    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.get(f"{settings.api_url}/clients", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur lors de la récupération des ID clients : {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Erreur de connexion lors de la récupération des ID clients : {e}")
        return []

@st.cache_data(ttl=30)
def get_api_logs(limit: int = 100):
    """Récupère les logs de l'API avec une limite."""
    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        url = f"{settings.api_url}/api-logs?limit={limit}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Erreur lors de la récupération des logs : {response.status_code} - {response.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur de connexion lors de la récupération des logs : {e}")
        return pd.DataFrame()

@st.cache_data(ttl=30)
def get_drift_reports_list():
    """Récupère la liste des rapports de dérive disponibles."""
    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.get(f"{settings.api_url}/drift-reports", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur lors de la récupération de la liste des rapports : {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Erreur de connexion lors de la récupération de la liste des rapports : {e}")
        return []

@st.cache_data(ttl=3600)
def get_drift_report_detail(report_id):
    """Récupère le contenu HTML d'un rapport de dérive spécifique."""
    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.get(f"{settings.api_url}/drift-reports/{report_id}", headers=headers)
        if response.status_code == 200:
            return response.json()['report_html']
        else:
            st.error(f"Erreur lors de la récupération du rapport #{report_id} : {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion lors de la récupération du rapport #{report_id} : {e}")
        return None

def trigger_drift_report_generation():
    """Déclenche la génération d'un nouveau rapport de dérive via l'API."""
    with st.spinner("Génération du rapport en cours..."):
        try:
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            response = requests.post(f"{settings.api_url}/drift-reports", headers=headers)
            if response.status_code == 201:
                st.success("Rapport de dérive généré avec succès ! Le cache va être vidé pour rafraîchir la liste.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Échec de la génération du rapport : {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Erreur de connexion lors de la génération du rapport : {e}")


# --- Fonctions d'Authentification ---
def login(username, password):
    """Appelle l'API pour obtenir un token JWT."""
    try:
        response = requests.post(f"{settings.api_url}/auth", data={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state['token'] = response.json()['access_token']
            st.success("Connexion réussie !")
            st.rerun()
        else:
            error_detail = response.json().get('detail', 'Erreur inconnue.')
            st.error(f"Échec de l'authentification : {error_detail} (Code: {response.status_code})")
    except requests.exceptions.ConnectionError:
        st.error(f"Impossible de se connecter à l'API à l'adresse : {settings.api_url}")
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue : {e}")

def logout():
    """Déconnecte l'utilisateur."""
    if 'token' in st.session_state:
        del st.session_state['token']
    st.success("Vous avez été déconnecté.")

# --- Interface Principale ---
st.set_page_config(layout="wide", page_title="Dashboard de Scoring Crédit")

# --- Écran de Connexion ---
if 'token' not in st.session_state:
    st.title("Connexion au Dashboard de Scoring")
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur", value=settings.api_user or "")
        password = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Se connecter"):
            login(username, password)
else:
    # --- Dashboard Principal ---
    st.sidebar.title(f"Bienvenue, {settings.api_user}")
    st.sidebar.button("Se déconnecter", on_click=logout)
    st.title("Dashboard de Scoring Crédit - Prêt à Dépenser")

    tab1, tab2, tab3 = st.tabs(["Prédiction de Score", "Performance de l'API", "Analyse de Dérive"])

    # --- Onglet 1: Prédiction ---
    with tab1:
        st.header("Calculer le score d'un client")
        client_ids = get_client_ids()
        if not client_ids:
            st.warning("Aucun ID client disponible ou erreur lors de la récupération.")
        else:
            selected_client_id = st.selectbox("Sélectionnez un ID Client", options=client_ids)
            if st.button("Obtenir le Score", type="primary"):
                with st.spinner("Appel de l'API en cours..."):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                        response = requests.post(f"{settings.api_url}/predict/{selected_client_id}", headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            st.success("Prédiction reçue avec succès !")
                            col1, col2 = st.columns(2)
                            col1.metric(label="Score de Risque", value=f"{data['prediction_probability']:.2%}")
                            col2.metric(label="Décision Suggérée", value=data['prediction_decision'])
                        else:
                            st.error(f"Erreur de l'API : {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"Une erreur inattendue est survenue : {e}")

    # --- Onglet 2: Performance ---
    with tab2:
        st.header("Monitoring de Performance de l'API")

        if st.checkbox("Charger l'historique complet des logs"):
            logs_df = get_api_logs(limit=0)
        else:
            st.info("Affichage des 100 derniers logs. Cochez la case ci-dessus pour voir l'historique complet.")
            logs_df = get_api_logs()

        if not logs_df.empty:
            logs_df['request_timestamp'] = pd.to_datetime(logs_df['request_timestamp']).dt.tz_localize(None)
            st.subheader("Filtres")
            min_date, max_date = logs_df['request_timestamp'].min().date(), logs_df['request_timestamp'].max().date()
            start_date = st.date_input("Date de début", min_date, min_value=min_date, max_value=max_date)
            end_date = st.date_input("Date de fin", max_date, min_value=start_date, max_value=max_date)
            start_datetime, end_datetime = datetime.combine(start_date, time.min), datetime.combine(end_date, time.max)
            filtered_logs = logs_df[(logs_df['request_timestamp'] >= start_datetime) & (logs_df['request_timestamp'] <= end_datetime)]
            st.divider()
            if not filtered_logs.empty:
                st.subheader("Statistiques sur la période")
                col1, col2, col3 = st.columns(3)
                col1.metric("Nombre de requêtes", len(filtered_logs))
                col2.metric("Temps d'inférence moyen", f"{filtered_logs['inference_time_ms'].mean():.2f} ms")
                col3.metric("Taux de succès", f"{(filtered_logs['http_status_code'] == 200).mean():.2%}")
                st.subheader("Évolution des temps d'inférence")
                st.line_chart(filtered_logs.set_index('request_timestamp')['inference_time_ms'])
                st.subheader("Détail des appels")
                st.dataframe(filtered_logs, use_container_width=True)
            else:
                st.info("Aucune donnée disponible pour la période sélectionnée.")
        else:
            st.info("Aucun log de performance disponible pour le moment.")

    # --- Onglet 3: Analyse de Dérive ---
    with tab3:
        st.header("Analyse de la Dérive des Données (Data Drift)")
        if st.button("Générer un nouveau Rapport de Dérive", type="secondary"):
            trigger_drift_report_generation()
        st.divider()
        reports = get_drift_reports_list()
        if reports:
            report_options = {f"Rapport #{r['id']} - {r['report_timestamp']}": r['id'] for r in reports}
            selected_report_display = st.selectbox("Sélectionnez un rapport", options=report_options.keys())
            if selected_report_display:
                report_id = report_options[selected_report_display]
                with st.spinner("Chargement du rapport..."):
                    report_html = get_drift_report_detail(report_id)
                    if report_html:
                        st.components.v1.html(report_html, height=600, scrolling=True)

                        # --- AJOUT DE LA FONCTIONNALITÉ DE TÉLÉCHARGEMENT ---
                        st.divider()
                        st.subheader("Exporter le rapport")

                        # Crée un nom de fichier propre à partir de l'option sélectionnée
                        clean_filename = selected_report_display.replace(' ', '_').replace(':', '').replace('#', 'id')

                        st.download_button(
                           label="📥 Télécharger ce rapport (HTML)",
                           data=report_html.encode("utf-8"),
                           file_name=f"{clean_filename}.html",
                           mime="text/html",
                           help="Cliquez pour télécharger le rapport actuellement affiché au format HTML."
                        )
        else:
            st.info("Aucun rapport de dérive n'a été généré pour le moment.")
