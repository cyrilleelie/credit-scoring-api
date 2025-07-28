# src/dashboard/app_dashboard.py

import streamlit as st
import pandas as pd
import requests
import warnings
import os
import sys
from datetime import datetime

# --- Bloc d'initialisation du chemin (pour une exécution directe) ---
# Permet de lancer le script directement tout en conservant les imports absolus
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.config import settings

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

# --- Fonctions refactorisées pour utiliser l'API ---

def get_auth_headers():
    """Retourne les en-têtes d'autorisation si un token existe."""
    if 'token' in st.session_state:
        return {"Authorization": f"Bearer {st.session_state['token']}"}
    st.error("Session expirée. Veuillez vous reconnecter.")
    st.session_state.clear()
    st.rerun()
    return None

@st.cache_data(ttl=600) # Met en cache les IDs pendant 10 minutes
def get_client_ids_from_api():
    """Récupère la liste des ID clients via l'API."""
    headers = get_auth_headers()
    if not headers: return []
    try:
        response = requests.get(f"{settings.api_url}/clients", headers=headers)
        response.raise_for_status() # Lève une erreur pour les statuts 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des ID clients : {e}")
        return []

# --- Fonctions d'Authentification ---
def login(username, password):
    """Appelle l'API pour obtenir un token JWT."""
    try:
        response = requests.post(
            f"{settings.api_url}/auth",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            st.session_state['token'] = response.json()['access_token']
            st.success("Connexion réussie !")
            st.rerun()
        else:
            # Affiche une erreur plus détaillée depuis la réponse de l'API
            error_detail = response.json().get('detail', 'Erreur inconnue.')
            st.error(f"Échec de l'authentification : {error_detail}")
    except requests.exceptions.ConnectionError:
        st.error("Impossible de se connecter à l'API. Vérifiez qu'elle est en cours d'exécution.")

def logout():
    """Déconnecte l'utilisateur."""
    if 'token' in st.session_state:
        del st.session_state['token']
    st.rerun()

# --- Interface Principale ---
st.set_page_config(layout="wide", page_title="Dashboard de Scoring Crédit")

if 'token' not in st.session_state:
    st.title("Connexion au Dashboard de Scoring")
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur", value=settings.api_user)
        password = st.text_input("Mot de passe", type="password", value=settings.api_password)
        if st.form_submit_button("Se connecter"):
            login(username, password)
else:
    # --- Dashboard Principal (si connecté) ---
    st.sidebar.title("Bienvenue")
    st.sidebar.button("Se déconnecter", on_click=logout)
    st.title("Dashboard de Scoring Crédit")

    tab1, tab2, tab3 = st.tabs(["Prédiction de Score", "Performance de l'API", "Analyse de Dérive"])

    # --- Onglet 1: Prédiction de Score ---
    with tab1:
        st.header("Calculer le score d'un client")
        client_ids = get_client_ids_from_api()
        if not client_ids:
            st.warning("Aucun ID client n'a pu être chargé depuis l'API.")
        else:
            selected_client_id = st.selectbox("Sélectionnez un ID Client", options=client_ids)
            if st.button("Obtenir le Score", type="primary"):
                headers = get_auth_headers()
                if selected_client_id and headers:
                    try:
                        response = requests.post(f"{settings.api_url}/predict/{selected_client_id}", headers=headers)
                        response.raise_for_status()
                        data = response.json()
                        st.success("Prédiction reçue avec succès !")
                        col1, col2 = st.columns(2)
                        col1.metric("Score de Risque", f"{data['prediction_probability']:.2%}")
                        col2.metric("Décision Suggérée", data['prediction_decision'])
                    except requests.exceptions.RequestException as e:
                        st.error(f"Erreur de l'API : {e.response.json().get('detail') if e.response else e}")

    # --- Onglet 2: Performance de l'API ---
    with tab2:
        st.header("Monitoring de Performance de l'API")
        headers = get_auth_headers()
        if headers:
            try:
                response = requests.get(f"{settings.api_url}/api-logs", headers=headers)
                response.raise_for_status()
                logs_data = response.json()
                if not logs_data:
                    st.info("Aucun log de performance disponible pour le moment.")
                else:
                    logs_df = pd.DataFrame(logs_data)
                    logs_df['request_timestamp'] = pd.to_datetime(logs_df['request_timestamp'])

                    st.subheader("Statistiques sur les 1000 derniers appels")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Nombre de requêtes", f"{len(logs_df)}")
                    col2.metric("Temps d'inférence moyen", f"{logs_df['inference_time_ms'].mean():.2f} ms")
                    col3.metric("Taux de succès", f"{(logs_df['http_status_code'] == 200).mean():.2%}")

                    st.subheader("Évolution des temps d'inférence")
                    st.line_chart(logs_df.set_index('request_timestamp')['inference_time_ms'])

                    st.subheader("Détail des appels")
                    st.dataframe(logs_df, use_container_width=True)
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur lors du chargement des logs : {e}")

    # --- Onglet 3: Analyse de Dérive ---
    with tab3:
        st.header("Analyse de la Dérive des Données")
        if st.button("Générer un nouveau Rapport de Dérive", type="secondary"):
            headers = get_auth_headers()
            if headers:
                with st.spinner("Génération du rapport en cours... Cette opération peut prendre du temps."):
                    try:
                        response = requests.post(f"{settings.api_url}/drift-reports", headers=headers)
                        response.raise_for_status()
                        st.success("Rapport de dérive généré avec succès ! Rechargez la liste ci-dessous.")
                        st.cache_data.clear() # Vide le cache pour recharger la liste des rapports
                    except requests.exceptions.RequestException as e:
                        st.error(f"Erreur lors de la génération du rapport : {e.response.json().get('detail') if e.response else e}")
        st.divider()

        headers = get_auth_headers()
        if headers:
            try:
                response = requests.get(f"{settings.api_url}/drift-reports", headers=headers)
                response.raise_for_status()
                reports_list = response.json()
                if not reports_list:
                    st.info("Aucun rapport de dérive disponible.")
                else:
                    report_options = {f"Rapport #{r['id']} - {r['report_timestamp']}": r['id'] for r in reports_list}
                    selected_report = st.selectbox("Sélectionnez un rapport à afficher", options=list(report_options.keys()))
                    if selected_report:
                        report_id = report_options[selected_report]
                        resp_html = requests.get(f"{settings.api_url}/drift-reports/{report_id}", headers=headers)
                        resp_html.raise_for_status()
                        st.components.v1.html(resp_html.json()['report_html'], height=600, scrolling=True)
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur lors du chargement des rapports : {e}")
