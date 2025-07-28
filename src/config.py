# src/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # --- Base de Données ---
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    
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
    train_data_file: str
    test_data_file: str

    @property
    def database_url(self) -> str:
        """Génère l'URL de connexion à la base de données."""
        # Encode le mot de passe pour qu'il soit sûr dans une URL
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    # Configuration pour Pydantic V2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Instance unique des paramètres
settings = Settings()
