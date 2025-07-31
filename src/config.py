# src/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class Settings(BaseSettings):
    # --- Base de Données ---
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    # Nouvelle variable pour contrôler le mode SSL (optionnelle)
    db_ssl_mode: Optional[str] = None
    
    # --- Sécurité JWT & API ---
    api_url: str
    api_user: Optional[str] = None
    api_password: Optional[str] = None
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # --- Modèle & Métier ---
    decision_threshold: float
    model_path: str
    
    # --- Chemins vers les données (optionnels) ---
    train_data_file: Optional[str] = None
    test_data_file: Optional[str] = None

    @property
    def database_url(self) -> str:
        """Génère l'URL de connexion à la base de données avec un mot de passe encodé."""
        encoded_password = urllib.parse.quote_plus(self.db_password)
        url = f"postgresql://{self.db_user}:{encoded_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        
        # Ajoute le paramètre SSL uniquement s'il est spécifié dans l'environnement
        if self.db_ssl_mode:
            url += f"?sslmode={self.db_ssl_mode}"
            
        return url

    # Configuration pour Pydantic V2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Instance unique des paramètres
settings = Settings()
