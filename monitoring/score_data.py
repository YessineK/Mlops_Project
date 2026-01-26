import os
import pandas as pd
import numpy as np
import joblib

TARGET_COL = "Attrition_Flag"
TARGET_BIN = "churn"
PRED_COL = "prediction"
PROBA_COL = "proba"

EPS = 1e-9  # éviter division par 0

def to_bin_label(s: pd.Series) -> pd.Series:
    return (s.astype(str).str.strip() == "Attrited Customer").astype(int)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

def add_engineered_features(X: pd.DataFrame) -> pd.DataFrame:
    """
    Recrée les features attendues par ton preprocessor :
    - utilisation_per_age
    - tenure_per_age
    - credit_lim_per_age
    - total_trans_amt_per_credit_lim
    - total_trans_ct_per_credit_lim
    """
    X = X.copy()

    # Assurer la présence des colonnes de base
    required = [
        "customer_age",
        "months_on_book",
        "credit_limit",
        "avg_utilization_ratio",
        "total_trans_amt",
        "total_trans_ct",
    ]
    missing_base = [c for c in required if c not in X.columns]
    if missing_base:
        raise ValueError(f"Missing base columns needed for feature engineering: {missing_base}")

    age = X["customer_age"].astype(float).replace(0, np.nan)
    credit = X["credit_limit"].astype(float).replace(0, np.nan)

    X["utilisation_per_age"] = X["avg_utilization_ratio"].astype(float) / (age + EPS)
    X["tenure_per_age"] = X["months_on_book"].astype(float) / (age + EPS)
    X["credit_lim_per_age"] = credit / (age + EPS)

    X["total_trans_amt_per_credit_lim"] = X["total_trans_amt"].astype(float) / (credit + EPS)
    X["total_trans_ct_per_credit_lim"] = X["total_trans_ct"].astype(float) / (credit + EPS)

    # Remplacer inf/NaN si besoin
    X = X.replace([np.inf, -np.inf], np.nan)

    return X

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))

    # modèle dans processors/models
    models_dir = os.path.join(project_root, "backend", "src", "processors", "models")
    model_path = os.path.join(models_dir, "best_model_final.pkl")

    # preprocessor dans processors/
    preprocessor_path = os.path.join(project_root, "backend", "src", "processors", "preprocessor.pkl")

    data_dir = os.path.join(base_dir, "data")
    ref_path = os.path.join(data_dir, "reference_data.csv")
    cur_path = os.path.join(data_dir, "current_data.csv")

    for p in [model_path, preprocessor_path, ref_path, cur_path]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing file: {p}")

    print("Loading model + preprocessor...")
    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    print("Loading reference/current data...")
    ref = pd.read_csv(ref_path)
    cur = pd.read_csv(cur_path)

    for name, df in [("reference", ref), ("current", cur)]:
        print(f"Scoring {name} data...")

        if TARGET_COL not in df.columns:
            raise ValueError(f"Missing '{TARGET_COL}' in {name} data")

        df[TARGET_BIN] = to_bin_label(df[TARGET_COL])

        # X brut
        X = df.drop(columns=[TARGET_COL, TARGET_BIN, PRED_COL, PROBA_COL], errors="ignore")
        X = normalize_columns(X)

        # Feature engineering (IMPORTANT)
        X = add_engineered_features(X)

        # Transform + predict
        Xp = preprocessor.transform(X)

        y_pred = model.predict(Xp)
        df[PRED_COL] = pd.Series(y_pred).astype(int)

        if hasattr(model, "predict_proba"):
            df[PROBA_COL] = model.predict_proba(Xp)[:, 1]
        else:
            df[PROBA_COL] = None

    ref.to_csv(ref_path, index=False)
    cur.to_csv(cur_path, index=False)

    print("✅ Done. Added columns:", [TARGET_BIN, PRED_COL, PROBA_COL])

if __name__ == "__main__":
    main()
