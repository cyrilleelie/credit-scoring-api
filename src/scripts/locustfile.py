# src/scripts/locustfile.py

import random
import os
import sys
from locust import HttpUser, task, between, events
from sqlalchemy import create_engine, text

# --- Bloc d'initialisation du chemin ---
# Permet de lancer le script tout en conservant les imports absolus
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.config import settings

# --- Variable globale pour stocker les ID clients ---
# Cette liste sera remplie une seule fois au début du test.
CLIENT_IDS = []

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Cette fonction est exécutée une seule fois au démarrage du test Locust.
    Elle se connecte à la BDD pour récupérer tous les ID clients.
    """
    print("--- Démarrage du test : Récupération des ID clients depuis la BDD ---")
    try:
        engine = create_engine(settings.database_url)
        with engine.connect() as connection:
            query = text("SELECT sk_id_curr FROM test_data;")
            result = connection.execute(query)
            # On stocke les IDs dans la variable globale
            global CLIENT_IDS
            CLIENT_IDS = [row[0] for row in result]
        
        if CLIENT_IDS:
            print(f"--- {len(CLIENT_IDS)} ID clients chargés avec succès. Prêt à lancer le test. ---")
        else:
            print("--- ATTENTION : Aucun ID client n'a été chargé. Le test de prédiction échouera. ---")

    except Exception as e:
        print(f"--- ERREUR CRITIQUE : Impossible de se connecter à la BDD pour charger les ID clients : {e} ---")
        # On arrête le test si on ne peut pas charger les données nécessaires
        environment.runner.quit()


class APIUser(HttpUser):
    """
    Utilisateur virtuel qui simule le comportement d'un client de l'API.
    """
    wait_time = between(1, 3)  # Temps d'attente aléatoire entre 1 et 3 secondes entre chaque tâche
    token = None
    
    def on_start(self):
        """
        Appelé une fois au démarrage de chaque utilisateur virtuel pour s'authentifier.
        """
        if settings.api_user and settings.api_password:
            response = self.client.post(
                "/auth", 
                data={"username": settings.api_user, "password": settings.api_password}
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
            else:
                print(f"Échec de l'authentification pour un utilisateur Locust. Statut : {response.status_code}")
        else:
            print("API_USER ou API_PASSWORD non configuré. L'utilisateur ne peut pas s'authentifier.")

    @task
    def get_prediction(self):
        """
        Tâche principale : appeler l'endpoint de prédiction avec un ID client aléatoire.
        """
        # On s'assure que l'utilisateur est bien authentifié ET que la liste des clients a été chargée
        if self.token and CLIENT_IDS:
            # Choisit un ID client au hasard dans la liste globale
            random_client_id = random.choice(CLIENT_IDS)
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # L'argument `name` permet de regrouper les statistiques dans l'interface Locust
            self.client.post(
                f"/predict/{random_client_id}", 
                headers=headers, 
                name="/predict/[client_id]"
            )
