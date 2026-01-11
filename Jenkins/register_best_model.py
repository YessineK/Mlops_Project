import os
import mlflow
import shutil
import dagshub
import pickle
from pathlib import Path
from dotenv import load_dotenv

# Load args
# Calculate paths relative to this script
# this file is at Projects/MLOps/Jenkins/register_best_model.py
# Root is at Projects/MLOps/ (2 levels up)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
# Configuration DagsHub token
DAGSHUB_TOKEN = 'f460bc1b164b8e147ccb2a8fc4208ae6075c0514'
os.environ['MLFLOW_TRACKING_USERNAME'] = 'karrayyessine1'
os.environ['MLFLOW_TRACKING_PASSWORD'] = DAGSHUB_TOKEN

# Config
DAGSHUB_USERNAME = os.getenv('DAGSHUB_USER', 'karrayyessine1')
DAGSHUB_REPO = os.getenv('DAGSHUB_REPO', 'mlops-fraud-detection')
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', f"https://dagshub.com/{DAGSHUB_USERNAME}/{DAGSHUB_REPO}.mlflow")
EXPERIMENT_NAME = "continuous_training_pipeline"

# Target path for the test script
# WARNING: test_fraud_scenario.py hardcodes 'Best_Fraud_LightGBM'. 
# We will use this directory even if the best model is not LightGBM to satisfy the test.
# Using BASE_DIR ensures we target the correct absolute path regardless of CWD.
DEST_DIR = BASE_DIR / "notebooks" / "model_registry" / "Best_Fraud_RandomForest"
DEST_PATH = DEST_DIR / "production.pkl"


def main():
    # Init
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    print(f"📡 Connecting to MLflow: {MLFLOW_TRACKING_URI}")
    
    # Get Experiment
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if not experiment:
        print(f"❌ Experiment '{EXPERIMENT_NAME}' not found.")
        return

    # Search Runs
    print("🔍 Searching for best model...")
    df = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="metrics.roc_auc > 0.5",
        order_by=["metrics.roc_auc DESC"],
        max_results=1
    )

    if df.empty:
        print("❌ No runs found.")
        return

    best_run = df.iloc[0]
    run_id = best_run.run_id
    model_name = best_run['params.model_name']
    roc_auc = best_run['metrics.roc_auc']

    print(f"🏆 Best Run Found:")
    print(f"   - Run ID: {run_id}")
    print(f"   - Model: {model_name}")
    print(f"   - ROC-AUC: {roc_auc:.4f}")

    # Register Model (Optional but requested)
    model_uri = f"runs:/{run_id}/model"
    reg_model_name = "Fraud_Detection_Production"
    try:
        print(f"📝 Registering model as '{reg_model_name}'...")
        mlflow.register_model(model_uri, reg_model_name)
    except Exception as e:
        print(f"⚠️ Registration warning: {e}")

    # Download Model for Testing/Deployment
    print(f"⬇️ Downloading model artifact to {DEST_PATH}...")
    
    # Ensure directory exists
    os.makedirs(DEST_DIR, exist_ok=True)
    
    # Download artifact to a temp location then move/rename
    local_path = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path="model/model.pkl")
    
    # Copy to the standardized 'production.pkl' location
    # Note: MLflow standard model artifact is often a directory or 'model.pkl' depending on logging
    # Here we assume standard logging which produces 'model.pkl' inside the artifact dir
    
    print(f"   - Artifact downloaded to: {local_path}")
    shutil.copy2(local_path, DEST_PATH)
    print(f"✅ Model saved to {DEST_PATH}")

if __name__ == "__main__":
    main()
