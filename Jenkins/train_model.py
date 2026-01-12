import os
import pandas as pd
import pickle
import mlflow
import mlflow.sklearn
from datetime import datetime
from pathlib import Path
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Configuration - Utiliser les variables d'environnement de Jenkins
BASE_DIR = Path(__file__).resolve().parent.parent

# Récupérer depuis les variables d'environnement
DAGSHUB_USERNAME = os.getenv('DAGSHUB_USER', 'karrayyessine1')
DAGSHUB_REPO = os.getenv('DAGSHUB_REPO', 'MLOps_Project')
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', f"https://dagshub.com/{DAGSHUB_USERNAME}/{DAGSHUB_REPO}.mlflow")

# IMPORTANT : Récupérer le token depuis les variables d'environnement
MLFLOW_TRACKING_USERNAME = os.getenv('MLFLOW_TRACKING_USERNAME', DAGSHUB_USERNAME)
MLFLOW_TRACKING_PASSWORD = os.getenv('MLFLOW_TRACKING_PASSWORD', '')

# Debug : afficher si le token existe (sans le montrer en entier)
print(f"📡 MLflow URI: {MLFLOW_TRACKING_URI}")
print(f"👤 Username: {MLFLOW_TRACKING_USERNAME}")
print(f"🔑 Password set: {'Yes' if MLFLOW_TRACKING_PASSWORD else 'No'}")
print(f"🔑 Password length: {len(MLFLOW_TRACKING_PASSWORD)}")

# Configurer MLflow avec authentification
os.environ['MLFLOW_TRACKING_USERNAME'] = MLFLOW_TRACKING_USERNAME
os.environ['MLFLOW_TRACKING_PASSWORD'] = MLFLOW_TRACKING_PASSWORD

# Initialize MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

print("🔄 Attempting to set experiment...")
mlflow.set_experiment("churn_prediction_continuous_training")
print("✅ Experiment set successfully!")

def load_data(filepath):
    """Charge les données preprocessées."""
    print(f"Chargement des données depuis {filepath}...")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier de données non trouvé: {filepath}")
    
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
    """Fonction principale d'entraînement."""
    
    # Chemin vers les données
    DATA_PATH = BASE_DIR / "notebooks" / "processors" / "preprocessed_data.pkl"
    
    # 1. Chargement
    try:
        data = load_data(DATA_PATH)
    except FileNotFoundError:
        print(f"Error: Data file not found at {DATA_PATH}")
        return

    X_train = data['X_train']
    X_test = data['X_test']
    y_train = data['y_train']
    y_test = data['y_test']

    print(f"Data loaded. Train shape: {X_train.shape}")

    # 2. Définition des modèles (sans CatBoost)
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        'XGBoost': XGBClassifier(n_estimators=100, random_state=42, n_jobs=-1, eval_metric='logloss'),
        'LightGBM': LGBMClassifier(n_estimators=100, random_state=42, n_jobs=-1, verbose=-1)
    }

    # 3. Entraînement et Tracking
    run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"🚀 Starting Continuous Training for {len(models)} models...")

    for name, model in models.items():
        print(f"Training {name}...")
        
        with mlflow.start_run(run_name=f"{name}_CT_{run_timestamp}"):
            # Log Params
            mlflow.log_params(model.get_params())
            mlflow.log_param('model_name', name)
            mlflow.log_param('stage', 'continuous_training')
            mlflow.log_param('timestamp', run_timestamp)
            
            # Train
            start_time = datetime.now()
            model.fit(X_train, y_train)
            duration = (datetime.now() - start_time).total_seconds()
            
            # Predict
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]
            
            # Metrics
            metrics = calculate_metrics(y_test, y_pred, y_proba)
            
            # Log Metrics
            for k, v in metrics.items():
                mlflow.log_metric(k, v)
            mlflow.log_metric('training_time_seconds', duration)
            
            print(f"  --> {name} finished. ROC-AUC: {metrics['roc_auc']:.4f} ({duration:.1f}s)")
            
            # Log Model
            mlflow.sklearn.log_model(model, "model")

    print("\n✅ Continuous Training Pipeline Completed.")

if __name__ == "__main__":
    train_and_track()