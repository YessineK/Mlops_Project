import os
import pandas as pd
import pickle
import mlflow
import mlflow.sklearn
import dagshub
from datetime import datetime
from pathlib import Path
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from dotenv import load_dotenv

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

DAGSHUB_USERNAME = os.getenv('DAGSHUB_USER', 'YessineK')
DAGSHUB_REPO = os.getenv('DAGSHUB_REPO', 'Mlops_Project')
MLFLOW_TRACKING_URI = f"https://dagshub.com/{DAGSHUB_USERNAME}/{DAGSHUB_REPO}.mlflow"

dagshub.init(repo_owner=DAGSHUB_USERNAME, repo_name=DAGSHUB_REPO, mlflow=True)
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("churn_prediction_training")

def load_data(filepath):
    """Charge les données preprocessées."""
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    return data

def calculate_metrics(y_true, y_pred, y_proba):
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'f1_score': f1_score(y_true, y_pred),
        'roc_auc': roc_auc_score(y_true, y_proba)
    }

def train_and_track():
    # Charger vos données
    DATA_PATH = BASE_DIR / "notebooks" / "processors" / "preprocessed_data.pkl"
    data = load_data(DATA_PATH)
    
    X_train = data['X_train']
    X_test = data['X_test']
    y_train = data['y_train']
    y_test = data['y_test']
    
    print(f"🚀 Starting training...")
    
    # Utiliser VOTRE meilleur modèle (LightGBM d'après vos fichiers)
    model = LGBMClassifier(n_estimators=100, random_state=42)
    
    with mlflow.start_run(run_name=f"LightGBM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        # Log params
        mlflow.log_params(model.get_params())
        mlflow.log_param('model_name', 'LightGBM')
        
        # Train
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        # Metrics
        metrics = calculate_metrics(y_test, y_pred, y_proba)
        
        # Log metrics
        for k, v in metrics.items():
            mlflow.log_metric(k, v)
        
        print(f"✅ Training completed. ROC-AUC: {metrics['roc_auc']:.4f}")
        
        # Log model
        mlflow.sklearn.log_model(model, "model")

if __name__ == "__main__":
    train_and_track()