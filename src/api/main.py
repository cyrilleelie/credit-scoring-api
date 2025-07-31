# src/api/main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
# --- CORRECTION APPLIQUÉE ICI ---
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import joblib
import pandas as pd
import numpy as np
import time
import json
from typing import List
import traceback

from src.database import models, schemas
from src.api import security
from src.database.database import get_db
from src.config import settings
from evidently import Report
from evidently.presets import DataDriftPreset
import tempfile
import os

app = FastAPI(title="API de Scoring Crédit", version="1.0")
model = joblib.load(settings.model_path)

# --- CONFIGURATION DU MIDDLEWARE CORS ---
# Permet à votre dashboard local de communiquer avec l'API sur Hugging Face.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines (pour le développement)
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autorise tous les en-têtes
)

# --- Dépendances (le reste du fichier est identique) ---
async def get_current_active_user(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except security.JWTError:
        raise credentials_exception
    
    user = security.get_user(db, username=username)
    if user is None or user.disabled:
        raise credentials_exception
    return user

# --- Fonctions utilitaires ---
def to_serializable(val):
    """Convertit les types de données NumPy en types Python standards."""
    if pd.isna(val):
        return None
    if isinstance(val, (np.int64, np.int32)):
        return int(val)
    if isinstance(val, (np.float64, np.float32)):
        return float(val)
    return val

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de Scoring Crédit"}

@app.post("/auth", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = security.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/predict/{client_id}", response_model=schemas.PredictionResponse)
def predict(
    request: Request,
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    start_time = time.time()
    db_client = db.query(models.ClientDataForTest).filter(models.ClientDataForTest.sk_id_curr == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail=f"Client ID {client_id} non trouvé.")

    client_data_df = pd.DataFrame([db_client.data])
    client_data_df = client_data_df.reindex(columns=model.feature_names_in_, fill_value=0)
    
    prediction_proba = float(model.predict_proba(client_data_df)[:, 1][0])
    decision = "Crédit Accordé" if prediction_proba < settings.decision_threshold else "Crédit Refusé"
    inference_time_ms = (time.time() - start_time) * 1000

    try:
        input_data_serializable = {k: to_serializable(v) for k, v in db_client.data.items()}
        
        log_entry = models.ApiLog(
            request_timestamp=datetime.now(),
            client_id=client_id,
            input_data=input_data_serializable,
            prediction_proba=prediction_proba,
            prediction_decision=decision,
            inference_time_ms=inference_time_ms,
            http_status_code=200
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"ERREUR lors de l'enregistrement du log : {e}")
        db.rollback()

    return {"client_id": client_id, "prediction_probability": prediction_proba, "prediction_decision": decision}

@app.get("/clients", response_model=List[int])
def get_all_client_ids(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    clients = db.query(models.ClientDataForTest.sk_id_curr).order_by(models.ClientDataForTest.sk_id_curr).all()
    return [client[0] for client in clients]

@app.get("/api-logs", response_model=List[schemas.ApiLog])
def get_api_logs(limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    query = db.query(models.ApiLog).order_by(models.ApiLog.request_timestamp.desc())
    if limit > 0:
        query = query.limit(limit)
    logs = query.all()
    
    for log in logs:
        if isinstance(log.input_data, str):
            log.input_data = json.loads(log.input_data)
            
    return logs

@app.get("/drift-reports", response_model=List[schemas.DriftReportInfo])
def get_drift_reports_list(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    reports = db.query(models.DriftReport.id, models.DriftReport.report_timestamp).order_by(models.DriftReport.report_timestamp.desc()).all()
    return reports

@app.get("/drift-reports/{report_id}", response_model=schemas.DriftReportDetail)
def get_drift_report_detail(report_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    report = db.query(models.DriftReport).filter(models.DriftReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rapport non trouvé.")
    return report

@app.post("/drift-reports", status_code=status.HTTP_201_CREATED)
def generate_drift_report(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    try:
        print("Début de la génération du rapport de dérive...")
        ref_query = db.query(models.TrainingData.data, models.TrainingData.target).limit(10000).statement
        reference_df = pd.read_sql(ref_query, db.bind)

        logs_query = db.query(models.ApiLog.input_data).statement
        current_logs_df = pd.read_sql(logs_query, db.bind)

        if current_logs_df.empty:
            raise HTTPException(status_code=400, detail="Aucun log de production trouvé.")

        reference_data = pd.DataFrame(list(reference_df['data']))
        reference_data['TARGET'] = reference_df['target']
        
        # --- CORRECTION APPLIQUÉE ICI ---
        # On convertit la chaîne JSON en dictionnaire avant de créer le DataFrame
        current_data_list = [json.loads(row) if isinstance(row, str) else row for row in current_logs_df['input_data']]
        current_data = pd.DataFrame(current_data_list)

        if 'TARGET' in reference_data.columns:
            reference_data.drop(columns=['TARGET'], inplace=True)
        
        common_cols = list(set(reference_data.columns) & set(current_data.columns))
        
        data_drift_report = Report(metrics=[DataDriftPreset()])
        data_drift_report_run = data_drift_report.run(reference_data=reference_data[common_cols], current_data=current_data[common_cols])

        fd, tmp_path = tempfile.mkstemp(suffix=".html")
        try:
            os.close(fd)
            data_drift_report_run.save_html(tmp_path)
            with open(tmp_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        finally:
            os.unlink(tmp_path)
        
        new_report = models.DriftReport(report_timestamp=datetime.now(), report_html=html_content)
        db.add(new_report)
        db.commit()

        return {"message": "Rapport de dérive généré avec succès."}

    except Exception as e:
        print("--- ERREUR LORS DE LA GÉNÉRATION DU RAPPORT DE DÉRIVE ---")
        traceback.print_exc()
        print("---------------------------------------------------------")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur : {e}")
