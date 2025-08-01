# src/scripts/profile_api.py

import cProfile
import pstats
import requests
import os
import sys

# --- Bloc d'initialisation du chemin ---
# Ajoute la racine du projet au PYTHONPATH pour que les imports
# comme `from src.config...` fonctionnent correctement lorsque le script est exécuté.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
# --- Fin du bloc ---

from src.config import settings

# --- Configuration du Test ---
# Ces valeurs sont chargées depuis votre fichier .env via la classe Settings
API_URL = settings.api_url
TEST_USER = settings.api_user
TEST_PASSWORD = settings.api_password

# Assurez-vous que cet ID client existe bien dans votre table `test_data`
# pour que les requêtes de prédiction réussissent.
CLIENT_ID_TO_TEST = 100001
NUM_REQUESTS = 10  # Nombre d'appels à l'API pour le profiling

def get_auth_token():
    """
    S'authentifie auprès de l'API pour récupérer un token d'accès JWT.
    Envoie une requête POST avec des données de formulaire (form data).
    """
    auth_url = f"{API_URL}/auth"
    print(f"Tentative d'authentification sur {auth_url}...")

    # Les données sont envoyées en tant que 'form data' (`application/x-www-form-urlencoded`),
    # ce qui est attendu par OAuth2PasswordRequestForm de FastAPI.
    form_data = {"username": TEST_USER, "password": TEST_PASSWORD}

    try:
        response = requests.post(auth_url, data=form_data)
        # Lève une exception HTTPError pour les réponses d'erreur (4xx ou 5xx).
        response.raise_for_status()
        print("Authentification réussie, token obtenu.")
        # Le token est extrait de la réponse JSON.
        return response.json()["access_token"]
    except requests.exceptions.HTTPError as e:
        print(f"ERREUR HTTP {e.response.status_code}: Échec de l'authentification.")
        print(f"Réponse de l'API : {e.response.text}")
        print("Vérifiez que vos identifiants dans le fichier .env sont corrects.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"ERREUR de connexion : Impossible de joindre l'API à l'adresse {auth_url}.")
        print(f"Assurez-vous que le serveur FastAPI est bien en cours d'exécution.")
        print(f"Détail de l'erreur : {e}")
        sys.exit(1)


def make_single_prediction(session, token):
    """
    Lance une requête de prédiction unique en utilisant une session existante.
    """
    predict_url = f"{API_URL}/predict/{CLIENT_ID_TO_TEST}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = session.post(predict_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERREUR lors de l'appel de prédiction à {predict_url} : {e}")
        return None

def run_profiling_session():
    """
    Fonction principale qui obtient un token et exécute
    une série d'appels à l'API pour les profiler.
    """
    token = get_auth_token()
    if not token:
        return

    # Utiliser une session requests permet de réutiliser la connexion TCP,
    # ce qui est plus efficace pour des appels multiples.
    with requests.Session() as session:
        print(f"Lancement de {NUM_REQUESTS} requêtes de prédiction pour le profiling...")
        for i in range(NUM_REQUESTS):
            print(f"  Appel {i + 1}/{NUM_REQUESTS}...")
            make_single_prediction(session, token)
    print("Profiling terminé.")

if __name__ == "__main__":
    # Initialise le profiler
    profiler = cProfile.Profile()
    profiler.enable()

    # Lance la fonction à analyser
    run_profiling_session()

    # Arrête le profiler et prépare les statistiques
    profiler.disable()
    # Trie les résultats par "temps cumulé" pour voir les fonctions les plus coûteuses
    stats = pstats.Stats(profiler).sort_stats('cumtime')

    # Affiche les résultats
    print("\n--- RÉSULTATS DU PROFILING (TOP 15 FONCTIONS PAR TEMPS CUMULÉ) ---")
    stats.print_stats(15)
