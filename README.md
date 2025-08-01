---
title: Credit Scoring API
emoji: 🤖
colorFrom: green
colorTo: blue
sdk: docker
app_port: 8000
pinned: false
---

# API de Scoring Crédit & Dashboard de Monitoring

[![Licence: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Ce projet a pour objectif de déployer un modèle de Machine Learning de scoring crédit via une API robuste (FastAPI) et de fournir un dashboard interactif (Streamlit) pour l'analyse et le monitoring en temps réel. L'ensemble de l'application est conçu pour être conteneurisable avec Docker et est supporté par une base de données PostgreSQL.

### 🚀 Accès à l'API Déployée

* **API & Documentation (Hugging Face) :** [API sur Hugging Face Spaces](https://cyrille-elie-credit-scoring-dashboard.hf.space/docs)

---

## 🏛️ Architecture

L'application est composée de trois services principaux conçus pour fonctionner ensemble :

1.  **Base de Données PostgreSQL** : Conteneurisée avec Docker pour le développement local et hébergée sur une base de données SQL Cloud (Google) pour la production.
2.  **API FastAPI** : Sert le modèle de scoring. Elle expose des endpoints sécurisés pour l'authentification et la prédiction, et enregistre chaque appel dans la base de données de production.
3.  **Dashboard Streamlit (Local)** : Fournit une interface utilisateur pour interagir avec l'API déployée, visualiser les performances et analyser la dérive des données. **Ce dashboard est conçu pour être lancé localement.**

## 📂 Structure du Projet

Le code est organisé en modules fonctionnels pour une meilleure clarté et maintenabilité.

```
credit-scoring-api/
├── .github/workflows/    # Workflows d'Intégration Continue (CI)
├── model_artifacts/      # Modèles entraînés (ignoré par Git)
├── src/                  # Code source de l'application
│   ├── api/              # Logique de l'API FastAPI
│   ├── config/           # Configuration de l'application
│   ├── dashboard/        # Logique du Dashboard Streamlit
│   │   └── app_dashboard.py
│   ├── database/         # Modèles de données et connexion BDD
│   └── scripts/          # Scripts utilitaires (init_db, profiling, etc.)
├── tests/                # Tests automatisés
│   ├── fixtures/         # Petits jeux de données pour les tests
│   └── test_api.py
├── .env.example          # Fichier d'exemple pour la configuration
├── .gitignore
├── docker-compose.yml    # Configuration pour lancer la BDD avec Docker
└── pyproject.toml        # Dépendances et configuration du projet (Poetry)
```

## 🚀 Installation et Lancement Local

Suivez ces étapes pour lancer l'application en environnement de développement.

### 1. Prérequis

* [Git](https://git-scm.com/)
* [Python 3.12+](https://www.python.org/)
* [Poetry](https://python-poetry.org/)
* [Docker](https://www.docker.com/) et Docker Compose

### 2. Cloner le Dépôt

```bash
git clone https://github.com/cyrilleelie/credit-scoring-api
cd credit-scoring-api
```

### 3. Fichier de Configuration

Créez votre fichier de configuration local à partir de l'exemple fourni.

```bash
cp .env.example .env
```

**Action requise :** Ouvrez le fichier `.env` et remplissez les valeurs.

* Pour un **test purement local**, utilisez les identifiants de la base de données Docker.
* Pour connecter le **dashboard local à l'API de production**, remplissez les variables avec les identifiants de votre base de données Cloud.

### 4. Installer les Dépendances

```bash
poetry install
```

### 5. Démarrer la Base de Données (pour test local)

Lancez le conteneur PostgreSQL en arrière-plan avec Docker Compose :

```bash
docker-compose up -d
```

### 6. Initialiser la Base de Données (pour test local)

Ce script crée le schéma de la base de données et y charge les données des clients.

```bash
poetry run python -m src.scripts.init_db
```

### 7. Lancer l'API FastAPI (pour test local)

Dans un premier terminal :

```bash
poetry run uvicorn src.api.main:app --reload
```

L'API sera accessible à l'adresse `http://127.0.0.1:8000`.

### 8. Lancer le Dashboard Streamlit

Dans un second terminal :

```bash
poetry run streamlit run src/dashboard/app_dashboard.py
```

Le dashboard sera accessible à l'adresse `http://localhost:8501`. Il se connectera à l'API et à la base de données configurées dans votre fichier `.env`.

## ✅ Tests

Pour lancer la suite de tests automatisés, exécutez la commande suivante depuis la racine du projet :

```bash
poetry run pytest
```

## 🔬 Analyse de Performance

Cette section décrit les outils utilisés pour mesurer et analyser la performance de l'API. **Assurez-vous que le serveur de l'API est en cours d'exécution** avant de lancer ces scripts.

### Profiling de l'API (`cProfile`)

```bash
poetry run python -m src.scripts.profile_api
```

### Test de Charge (`Locust`)

1.  **Lancez Locust :**
    ```bash
    poetry run locust -f src/scripts/locustfile.py --host="http://127.0.0.1:8000"
    ```
2.  **Ouvrez l'interface web de Locust** dans votre navigateur à l'adresse `http://localhost:8089`.
3.  **Configurez et démarrez un test** en spécifiant le nombre d'utilisateurs et le taux d'apparition.

---

### ⚖️ Conformité RGPD et Éthique

Ce projet a été développé dans le respect de la confidentialité des données.

* **Anonymisation** : Les données utilisées pour l'entraînement et les prédictions sont anonymisées. L'identifiant client est le seul moyen de relier une prédiction à une entité.
* **Transparence du Modèle** : Le dashboard permet de monitorer la dérive des données, assurant ainsi une surveillance continue du comportement du modèle pour détecter d'éventuels biais ou une dégradation de sa pertinence.
* **Droit à l'Oubli** : Bien que non implémentée, l'architecture permettrait d'ajouter une fonctionnalité pour supprimer les données d'un client de la base de données sur demande.
