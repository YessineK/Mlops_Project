import os
import mlflow
import shutil
import dagshub
import pickle
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

DAGSHUB_USERNAME = os.getenv('DAGSHUB_USER', 'YessineK')
DAGSHUB_REPO = os.getenv('DAGSHUB_REPO', 'Mlops_Project')
MLFLOW_TRACKING_URI = f"https://dagshub.com/{DAGSHUB_USERNAME}/{DAGSHUB_REPO}.mlflow"
EXPERIMENT_NAME = "churn_prediction_training"

# Destination pour le backend
DEST_DIR = BASE_DIR / "backend" / "src" / "processors" / "models"
DEST_PATH = DEST_DIR / "best_model_final.pkl"

def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    print(f"📡 Connecting to MLflow...")
    
    # Get experiment
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if not experiment:
        print(f"❌ Experiment '{EXPERIMENT_NAME}' not found.")
        return
    
    # Search best run
    print("🔍 Searching for best model...")
    df = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.roc_auc DESC"],
        max_results=1
    )
    
    if df.empty:
        print("❌ No runs found.")
        return
    
    best_run = df.iloc[0]
    run_id = best_run.run_id
    roc_auc = best_run['metrics.roc_auc']
    
    print(f"🏆 Best Run: {run_id}")
    print(f"   ROC-AUC: {roc_auc:.4f}")
    
    # Download model
    print(f"⬇️ Downloading model...")
    os.makedirs(DEST_DIR, exist_ok=True)
    
    local_path = mlflow.artifacts.download_artifacts(
        run_id=run_id, 
        artifact_path="model/model.pkl"
    )
    
    shutil.copy2(local_path, DEST_PATH)
    print(f"✅ Model saved to {DEST_PATH}")

if __name__ == "__main__":
    main()