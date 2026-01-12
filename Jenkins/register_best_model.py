import os
import mlflow
import shutil
import pickle
from pathlib import Path
from dotenv import load_dotenv

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# DagsHub Config
DAGSHUB_TOKEN = os.getenv('DAGSHUB_TOKEN', '2b2313d8f6c5cac7bd36505929faecedfdfb8ed4')
DAGSHUB_USERNAME = 'karrayyessine1'
DAGSHUB_REPO = 'MLOps_Project'

os.environ['MLFLOW_TRACKING_USERNAME'] = DAGSHUB_USERNAME
os.environ['MLFLOW_TRACKING_PASSWORD'] = DAGSHUB_TOKEN

MLFLOW_TRACKING_URI = f"https://dagshub.com/{DAGSHUB_USERNAME}/{DAGSHUB_REPO}.mlflow"
EXPERIMENT_NAME = "churn_prediction"

# Destination
DEST_DIR = BASE_DIR / "notebooks" / "processors" / "models"
DEST_PATH = DEST_DIR / "best_model_final.pkl"

def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    print(f"📡 Connecting to MLflow: {MLFLOW_TRACKING_URI}")
    
    # Get Experiment
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if not experiment:
        print(f"❌ Experiment '{EXPERIMENT_NAME}' not found.")
        return

    # Search Best Model
    print("🔍 Searching for best model...")
    df = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string="metrics.roc_auc > 0.9",
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

    # Register Model
    model_uri = f"runs:/{run_id}/model"
    reg_model_name = "Churn_Prediction_Production"
    
    try:
        print(f"📝 Registering model as '{reg_model_name}'...")
        mlflow.register_model(model_uri, reg_model_name)
        print("✅ Model registered")
    except Exception as e:
        print(f"⚠️ Registration warning: {e}")

    print(f"✅ Best model: {model_name} (ROC-AUC: {roc_auc:.4f})")

if __name__ == "__main__":
    main()