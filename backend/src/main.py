# api/main.py
import os
import sys
import pandas as pd
import numpy as np
import pickle
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import io

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Bank Churn Prediction API",
    description="API pour prédire le churn des clients bancaires",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CONFIGURATION & GLOBAL VARIABLES
# ============================================================================

PROCESSORS_DIR = os.path.join(os.path.dirname(__file__), "processors")
MODEL_PATH = os.path.join(PROCESSORS_DIR, "models", "best_model_final.pkl")
PREPROCESSOR_PATH = os.path.join(PROCESSORS_DIR, "preprocessor.pkl")
FEATURE_NAMES_PATH = os.path.join(PROCESSORS_DIR, "feature_names.pkl")
METADATA_PATH = os.path.join(PROCESSORS_DIR, "models", "best_model_final_metadata.pkl")

# Global variables
model = None
preprocessor = None
feature_names = None
model_metadata = {}


# ============================================================================
# PYDANTIC MODELS - SCHEMA D'ENTRÉE
# ============================================================================

class CustomerInput(BaseModel):
    """
    Schéma pour la prédiction d'un client unique
    """
    customer_age: int = Field(45, ge=18, le=100, description="Âge du client")
    gender: str = Field("M", description="Genre (M/F)")
    dependent_count: int = Field(3, ge=0, le=10, description="Nombre de personnes à charge")
    education_level: str = Field("Graduate", description="Niveau d'éducation")
    marital_status: str = Field("Married", description="Statut marital")
    income_category: str = Field("$60K - $80K", description="Catégorie de revenu")
    card_category: str = Field("Blue", description="Type de carte")
    months_on_book: int = Field(39, ge=0, description="Ancienneté en mois")
    total_relationship_count: int = Field(5, ge=1, le=6, description="Nombre de produits")
    months_inactive_12_mon: int = Field(1, ge=0, le=12, description="Mois d'inactivité (12 derniers mois)")
    contacts_count_12_mon: int = Field(3, ge=0, description="Nombre de contacts (12 derniers mois)")
    credit_limit: float = Field(12691.0, ge=0, description="Limite de crédit")
    total_revolving_bal: int = Field(777, ge=0, description="Solde revolving total")
    avg_open_to_buy: float = Field(11914.0, ge=0, description="Crédit disponible moyen")
    total_amt_chng_q4_q1: float = Field(1.335, description="Changement montant Q4/Q1")
    total_trans_amt: int = Field(1144, ge=0, description="Montant total des transactions")
    total_trans_ct: int = Field(42, ge=0, description="Nombre total de transactions")
    total_ct_chng_q4_q1: float = Field(1.625, description="Changement nombre transactions Q4/Q1")
    avg_utilization_ratio: float = Field(0.061, ge=0, le=1, description="Taux d'utilisation moyen")

    class Config:
        schema_extra = {
            "example": {
                "customer_age": 45,
                "gender": "M",
                "dependent_count": 3,
                "education_level": "Graduate",
                "marital_status": "Married",
                "income_category": "$60K - $80K",
                "card_category": "Blue",
                "months_on_book": 39,
                "total_relationship_count": 5,
                "months_inactive_12_mon": 1,
                "contacts_count_12_mon": 3,
                "credit_limit": 12691.0,
                "total_revolving_bal": 777,
                "avg_open_to_buy": 11914.0,
                "total_amt_chng_q4_q1": 1.335,
                "total_trans_amt": 1144,
                "total_trans_ct": 42,
                "total_ct_chng_q4_q1": 1.625,
                "avg_utilization_ratio": 0.061
            }
        }


# ============================================================================
# PREPROCESSING FUNCTIONS
# ============================================================================

def preprocess_raw_churn(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique le preprocessing churn (feature engineering)
    Reprend la logique du notebook preprocessing.ipynb
    """
    df = df.copy()
    
    # Lowercase columns
    df.columns = df.columns.str.lower()
    
    # Convert to categorical
    categorical_cols = ['gender', 'education_level', 'marital_status', 'income_category', 'card_category']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    # Fill missing values (si nécessaire)
    if 'marital_status' in df.columns:
        df['marital_status'] = df['marital_status'].replace('Unknown', 'Married')
    
    if 'income_category' in df.columns:
        df['income_category'] = df['income_category'].replace('Unknown', 'Less than $40K')
    
    # Feature Engineering (engineered features du notebook)
    if 'months_on_book' in df.columns and 'customer_age' in df.columns:
        df['tenure_per_age'] = df['months_on_book'] / (df['customer_age'] * 12)
    
    if 'avg_utilization_ratio' in df.columns and 'customer_age' in df.columns:
        df['utilisation_per_age'] = df['avg_utilization_ratio'] / df['customer_age']
    
    if 'credit_limit' in df.columns and 'customer_age' in df.columns:
        df['credit_lim_per_age'] = df['credit_limit'] / df['customer_age']
    
    if 'total_trans_amt' in df.columns and 'credit_limit' in df.columns:
        df['total_trans_amt_per_credit_lim'] = df['total_trans_amt'] / df['credit_limit']
    
    if 'total_trans_ct' in df.columns and 'credit_limit' in df.columns:
        df['total_trans_ct_per_credit_lim'] = df['total_trans_ct'] / df['credit_limit']
    
    return df


def apply_preprocessor(df: pd.DataFrame, preprocessor, feature_names) -> np.ndarray:
    """
    Applique le ColumnTransformer sklearn
    """
    # Transform avec le preprocessor (StandardScaler + OneHotEncoder)
    X_transformed = preprocessor.transform(df)
    
    # Vérifier la cohérence des features
    if feature_names is not None:
        expected_features = len(feature_names)
        actual_features = X_transformed.shape[1]
        
        if expected_features != actual_features:
            print(f"⚠️ Warning: Expected {expected_features} features, got {actual_features}")
    
    return X_transformed


# ============================================================================
# STARTUP EVENT - CHARGEMENT DU MODÈLE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    global model, preprocessor, feature_names, model_metadata
    
    print("="*80)
    print("🚀 DÉMARRAGE DE L'API CHURN PREDICTION")
    print("="*80)
    
    # 1. Load Preprocessor
    try:
        with open(PREPROCESSOR_PATH, 'rb') as f:
            preprocessor = pickle.load(f)
        print(f"✅ Preprocessor chargé: {PREPROCESSOR_PATH}")
    except Exception as e:
        print(f"❌ Erreur chargement preprocessor: {e}")
        preprocessor = None
    
    # 2. Load Feature Names
    try:
        with open(FEATURE_NAMES_PATH, 'rb') as f:
            feature_names = pickle.load(f)
        print(f"✅ Feature names chargés: {len(feature_names)} features")
    except Exception as e:
        print(f"❌ Erreur chargement feature_names: {e}")
        feature_names = None
    
    # 3. Load Model
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print(f"✅ Modèle chargé: {MODEL_PATH}")
    except Exception as e:
        print(f"❌ Erreur chargement modèle: {e}")
        model = None
    
    # 4. Load Metadata
    try:
        with open(METADATA_PATH, 'rb') as f:
            model_metadata = pickle.load(f)
        print(f"✅ Métadonnées chargées")
        print(f"   Modèle: {model_metadata.get('model_name')}")
        print(f"   ROC-AUC: {model_metadata.get('metrics', {}).get('roc_auc', 'N/A')}")
        print(f"   F1-Score: {model_metadata.get('metrics', {}).get('f1_score', 'N/A')}")
    except Exception as e:
        print(f"⚠️ Métadonnées non disponibles: {e}")
        model_metadata = {}
    
    print("="*80)
    
    if not model or not preprocessor:
        print("⚠️ API démarrée en mode dégradé (prédictions non disponibles)")
    else:
        print("✅ API prête pour les prédictions!")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    return {
        "message": "Bank Churn Prediction API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Vérification de l'état de l'API"""
    status = "healthy" if (model and preprocessor) else "degraded"
    
    return {
        "status": status,
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
        "feature_names_loaded": feature_names is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/model-info")
def get_model_info():
    """Informations sur le modèle chargé"""
    if not model_metadata:
        return {"error": "Métadonnées du modèle non disponibles"}
    
    return {
        "model_name": model_metadata.get('model_name'),
        "model_type": model_metadata.get('model_type'),
        "metrics": model_metadata.get('metrics'),
        "training_time_sec": model_metadata.get('training_time_sec'),
        "timestamp": model_metadata.get('timestamp'),
        "global_score": model_metadata.get('global_score')
    }


@app.get("/features")
def get_features():
    """Liste des features attendues"""
    if feature_names is None:
        return {"error": "Feature names non disponibles"}
    
    return {
        "total_features": len(feature_names),
        "feature_names": feature_names.tolist() if hasattr(feature_names, 'tolist') else list(feature_names)
    }


@app.post("/predict")
async def predict_single(customer: CustomerInput):
    """
    Prédiction pour un client unique
    """
    if not model or not preprocessor:
        raise HTTPException(status_code=503, detail="Service non disponible")
    
    try:
        # Convertir en DataFrame
        df_input = pd.DataFrame([customer.dict()])
        
        # 1. Feature Engineering
        df_processed = preprocess_raw_churn(df_input)
        
        # 2. Apply preprocessor (scaling + encoding)
        X = apply_preprocessor(df_processed, preprocessor, feature_names)
        
        # 3. Predict
        prediction = model.predict(X)[0]
        
        # 4. Predict proba (si disponible)
        proba = None
        if hasattr(model, 'predict_proba'):
            proba_array = model.predict_proba(X)[0]
            proba = {
                "non_churn": float(proba_array[0]),
                "churn": float(proba_array[1])
            }
        
        return {
            "prediction": int(prediction),
            "prediction_label": "Churn" if prediction == 1 else "Non-Churn",
            "probabilities": proba,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")


@app.post("/predict-batch")
async def predict_batch(customers: List[CustomerInput]):
    """
    Prédiction pour plusieurs clients
    """
    if not model or not preprocessor:
        raise HTTPException(status_code=503, detail="Service non disponible")
    
    try:
        # Convertir en DataFrame
        df_input = pd.DataFrame([c.dict() for c in customers])
        
        # 1. Feature Engineering
        df_processed = preprocess_raw_churn(df_input)
        
        # 2. Apply preprocessor
        X = apply_preprocessor(df_processed, preprocessor, feature_names)
        
        # 3. Predict
        predictions = model.predict(X)
        
        # 4. Predict proba
        probas = None
        if hasattr(model, 'predict_proba'):
            probas = model.predict_proba(X)
        
        # Format results
        results = []
        for i, pred in enumerate(predictions):
            result = {
                "index": i,
                "prediction": int(pred),
                "prediction_label": "Churn" if pred == 1 else "Non-Churn"
            }
            
            if probas is not None:
                result["probabilities"] = {
                    "non_churn": float(probas[i][0]),
                    "churn": float(probas[i][1])
                }
            
            results.append(result)
        
        return {
            "count": len(results),
            "predictions": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction batch: {str(e)}")


@app.post("/predict-csv")
async def predict_csv(file: UploadFile = File(...)):
    """
    Upload CSV, obtenir prédictions, télécharger résultat
    """
    if not model or not preprocessor:
        raise HTTPException(status_code=503, detail="Service non disponible")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Le fichier doit être un CSV")
    
    try:
        # Read CSV
        contents = await file.read()
        df_input = pd.read_csv(io.BytesIO(contents))
        
        print(f"📥 CSV reçu: {len(df_input)} lignes, {len(df_input.columns)} colonnes")
        
        # 1. Feature Engineering
        df_processed = preprocess_raw_churn(df_input)
        
        # 2. Apply preprocessor
        X = apply_preprocessor(df_processed, preprocessor, feature_names)
        
        # 3. Predict
        predictions = model.predict(X)
        
        # 4. Probabilities
        if hasattr(model, 'predict_proba'):
            probas = model.predict_proba(X)
            df_result = df_input.copy()
            df_result['churn_prediction'] = predictions
            df_result['proba_non_churn'] = probas[:, 0]
            df_result['proba_churn'] = probas[:, 1]
        else:
            df_result = df_input.copy()
            df_result['churn_prediction'] = predictions
        
        # Save to buffer
        output = io.StringIO()
        df_result.to_csv(output, index=False)
        output.seek(0)
        
        # Return file
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=churn_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur traitement CSV: {str(e)}")


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)