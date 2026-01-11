import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from preprocessing_fraud_class import PreprocessingFraud

# Configuration MLflow et DagsHub
# Configuration MLflow et DagsHub
DAGSHUB_USER = 'karrayyessine1'
DAGSHUB_REPO = 'mlops-fraud-detection'
DAGSHUB_TOKEN = 'f460bc1b164b8e147ccb2a8fc4208ae6075c0514'  # Token en dur

# Configurer les credentials
os.environ['MLFLOW_TRACKING_USERNAME'] = DAGSHUB_USER
os.environ['MLFLOW_TRACKING_PASSWORD'] = DAGSHUB_TOKEN

# Debug
print(f"🔍 Token: {DAGSHUB_TOKEN[:10]}...")
print(f"🔍 DEBUG - Token length: {len(DAGSHUB_TOKEN)}")
print(f"🔍 DEBUG - Token first 10 chars: {DAGSHUB_TOKEN[:10] if DAGSHUB_TOKEN else 'EMPTY'}")
print(f"🔍 DEBUG - MLFLOW_TRACKING_PASSWORD env: {os.getenv('MLFLOW_TRACKING_PASSWORD', 'NOT SET')[:10] if os.getenv('MLFLOW_TRACKING_PASSWORD') else 'NOT SET'}")
# Configurer les credentials
os.environ['MLFLOW_TRACKING_USERNAME'] = DAGSHUB_USER
os.environ['MLFLOW_TRACKING_PASSWORD'] = DAGSHUB_TOKEN

# Set tracking URI
MLFLOW_TRACKING_URI = f"https://dagshub.com/{DAGSHUB_USER}/{DAGSHUB_REPO}.mlflow"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

print(f"✅ MLflow configured: {MLFLOW_TRACKING_URI}")
print(f"✅ User: {DAGSHUB_USER}")

# Set experiment
mlflow.set_experiment("continuous_training_pipeline")
