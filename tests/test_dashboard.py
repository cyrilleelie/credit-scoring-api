# tests/test_dashboard.py

import pytest
import streamlit as st
from unittest.mock import patch

# --- CORRECTION APPLIQUÉE ICI ---
# On importe la fonction avec son nom correct
from src.dashboard.app_dashboard import get_client_ids
from src.config import settings

# --- Fixture pour nettoyer le cache de Streamlit avant chaque test ---
@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    """Garantit que les tests sont isolés les uns des autres."""
    st.cache_data.clear()
    st.cache_resource.clear()
    yield

def test_get_client_ids_success(requests_mock):
    """
    Teste que la fonction get_client_ids retourne une liste d'entiers
    quand l'API répond correctement.
    """
    # 1. Préparation (Arrange)
    # On simule la réponse de l'API
    expected_ids = [100001, 100002, 100003]
    requests_mock.get(f"{settings.api_url}/clients", json=expected_ids, status_code=200)
    
    # On simule la présence d'un token dans la session Streamlit
    with patch('streamlit.session_state', {'token': 'fake_token'}):
        # 2. Action (Act)
        # --- CORRECTION APPLIQUÉE ICI ---
        client_ids = get_client_ids()

    # 3. Vérification (Assert)
    assert client_ids == expected_ids

def test_get_client_ids_api_error(requests_mock):
    """
    Teste que la fonction retourne une liste vide en cas d'erreur 500 de l'API.
    """
    # 1. Préparation (Arrange)
    # On simule une erreur serveur de l'API
    requests_mock.get(f"{settings.api_url}/clients", status_code=500, text="Internal Server Error")
    
    with patch('streamlit.session_state', {'token': 'fake_token'}):
        # 2. Action (Act)
        # --- CORRECTION APPLIQUÉE ICI ---
        client_ids = get_client_ids()

    # 3. Vérification (Assert)
    # La fonction doit retourner une liste vide et ne pas planter
    assert client_ids == []

def test_get_client_ids_unauthorized():
    """
    Teste que la fonction retourne une liste vide si l'utilisateur n'est pas authentifié.
    """
    # 1. Préparation (Arrange)
    # On s'assure qu'il n'y a pas de token dans la session
    with patch('streamlit.session_state', {}):
        # 2. Action (Act)
        # --- CORRECTION APPLIQUÉE ICI ---
        client_ids = get_client_ids()

    # 3. Vérification (Assert)
    assert client_ids == []
