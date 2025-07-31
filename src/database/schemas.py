# src/database/schemas.py

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Schémas pour l'Authentification ---

class TokenData(BaseModel):
    username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Schéma pour la Prédiction ---

class PredictionResponse(BaseModel):
    client_id: int
    prediction_probability: float
    prediction_decision: str

# --- Schémas pour les Endpoints du Dashboard ---

# Schéma pour la sortie des logs de l'API
# Il est utilisé pour valider les données envoyées par l'endpoint /api-logs
class ApiLog(BaseModel):
    id: int
    request_timestamp: datetime
    client_id: Optional[int]
    input_data: Dict[str, Any]
    prediction_proba: float
    prediction_decision: str
    inference_time_ms: float
    http_status_code: int

    # Permet à Pydantic de lire les données depuis un objet SQLAlchemy
    class Config:
        from_attributes = True

# Schéma pour la liste des rapports de dérive
class DriftReportInfo(BaseModel):
    id: int
    report_timestamp: datetime

    class Config:
        from_attributes = True

# Schéma pour le détail d'un rapport de dérive (avec le contenu HTML)
class DriftReportDetail(BaseModel):
    id: int
    report_timestamp: datetime
    report_html: str

    class Config:
        from_attributes = True
