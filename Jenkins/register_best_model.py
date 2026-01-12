import os
import mlflow
import shutil
import pickle
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent

DAGSHUB_USERNAME = os.getenv('DAGSHUB_USER', 'karrayyessine1')
DAGSHUB_REPO = os.getenv('DAGSHUB_REPO', 'MLOps_Project')
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', f"https://dagshub.com/{DAGSHUB_USERNAME}/{DAGSHUB_REPO}.mlflow")
EXPERIMENT_NAME = "churn_prediction_continuous_training"

# Configurer les credentials
os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv('MLFLOW_TRACKING_USERNAME', DAGSHUB_USERNAME)
os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv('MLFLOW_TRACKING_PASSWORD', '')

# Destination pour le backend
DEST_DIR = BASE_DIR / "backend" / "src" / "processors" / "models"
DEST_PATH = DEST_DIR / "best_model_final.pkl"

def main():
    # Init MLflow
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    print(f"📡 Connecting to MLflow: {MLFLOW_TRACKING_URI}")
    
    # Get Experiment
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if not experiment:
        print(f"❌ Experiment '{EXPERIMENT_NAME}' not found.")
        return

    # Search Best Run
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
    model_name = best_run.get('params.model_name', 'Unknown')
    roc_auc = best_run['metrics.roc_auc']

    print(f"🏆 Best Run Found:")
    print(f"   - Run ID: {run_id}")
    print(f"   - Model: {model_name}")
    print(f"   - ROC-AUC: {roc_auc:.4f}")

    # Register Model (Optional)
    model_uri = f"runs:/{run_id}/model"
    reg_model_name = "Churn_Prediction_Production"
    try:
        print(f"📝 Registering model as '{reg_model_name}'...")
        mlflow.register_model(model_uri, reg_model_name)
    except Exception as e:
        print(f"⚠️ Registration warning: {e}")

    # Download Model
    print(f"⬇️ Downloading model artifact to {DEST_PATH}...")
    
    # Ensure directory exists
    os.makedirs(DEST_DIR, exist_ok=True)
    
    # Download artifact
    local_path = mlflow.artifacts.download_artifacts(
        run_id=run_id, 
        artifact_path="model/model.pkl"
    )
    
    # Copy to destination
    print(f"   - Artifact downloaded to: {local_path}")
    shutil.copy2(local_path, DEST_PATH)
    print(f"✅ Model saved to {DEST_PATH}")
    
    # Save metadata
    metadata = {
        'run_id': run_id,
        'model_name': model_name,
        'roc_auc': roc_auc,
        'timestamp': best_run.get('start_time', 'Unknown')
    }
    
    metadata_path = DEST_DIR / "best_model_final_metadata.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✅ Metadata saved to {metadata_path}")

if __name__ == "__main__":
    main()