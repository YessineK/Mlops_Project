import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score
)
import pickle

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# ============================================================================
# CONFIGURATION MLFLOW + DAGSHUB
# ============================================================================

DAGSHUB_USERNAME = 'karrayyessine1'
DAGSHUB_REPO = 'MLOps_Project'
DAGSHUB_TOKEN = '2b2313d8f6c5cac7bd36505929faecedfdfb8ed4'

# Set credentials AVANT de configurer MLflow
os.environ['MLFLOW_TRACKING_USERNAME'] = DAGSHUB_USERNAME
os.environ['MLFLOW_TRACKING_PASSWORD'] = DAGSHUB_TOKEN

# Configure MLflow
MLFLOW_TRACKING_URI = f"https://dagshub.com/{DAGSHUB_USERNAME}/{DAGSHUB_REPO}.mlflow"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

print("="*80)
print("🚀 CONTINUOUS TRAINING - CHURN PREDICTION")
print("="*80)
print(f"📡 MLflow URI: {MLFLOW_TRACKING_URI}")
print(f"👤 User: {DAGSHUB_USERNAME}")
print(f"🔑 Token: {DAGSHUB_TOKEN[:10]}...")

# Test connection
try:
    mlflow.set_experiment("continuous_training_pipeline")
    print("✅ MLflow connection successful!")
except Exception as e:
    print(f"❌ MLflow connection failed: {e}")
    sys.exit(1)

# ============================================================================
# LOAD DATA
# ============================================================================

print("\n📥 Loading preprocessed data...")

DATA_PATH = BASE_DIR / "notebooks" / "processors" / "preprocessed_data.pkl"

with open(DATA_PATH, 'rb') as f:
    data = pickle.load(f)

X_train = data['X_train']
X_test = data['X_test']
y_train = data['y_train']
y_test = data['y_test']

print(f"✅ Data loaded")
print(f"   Train: {X_train.shape}")
print(f"   Test: {X_test.shape}")

# ============================================================================
# TRAIN MODELS
# ============================================================================

models = {
    'RandomForest': RandomForestClassifier(
        n_estimators=100, 
        random_state=42, 
        n_jobs=-1
    ),
    'XGBoost': XGBClassifier(
        n_estimators=100, 
        random_state=42, 
        n_jobs=-1,
        eval_metric='logloss'
    ),
    'LightGBM': LGBMClassifier(
        n_estimators=100, 
        random_state=42, 
        n_jobs=-1,
        verbose=-1
    )
}

print("\n🤖 Training models...\n")

for model_name, model in models.items():
    print(f"📊 Training {model_name}...", end=" ")
    
    with mlflow.start_run(run_name=f"{model_name}_retrain"):
        # Train
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        # Metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_proba)
        }
        
        # Log to MLflow
        mlflow.log_param('model_name', model_name)
        mlflow.log_param('n_features', X_train.shape[1])
        mlflow.log_param('dataset', 'churn_retrain')
        
        for metric_name, metric_value in metrics.items():
            mlflow.log_metric(metric_name, metric_value)
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        print(f"ROC-AUC: {metrics['roc_auc']:.4f}")

print("\n✅ Training completed!")
print("🔗 View results: https://dagshub.com/karrayyessine1/MLOps_Project.mlflow")