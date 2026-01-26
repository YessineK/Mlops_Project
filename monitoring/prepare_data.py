import pandas as pd
import os
import subprocess
import sys


def prepare_data():
    # -----------------------------
    # PATHS
    # -----------------------------
    # On est déjà dans le dossier monitoring
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Reference = dataset de base
    reference_path = os.path.join(base_dir, "data", "churn2.csv")

    # Current = batch "prod" (tu peux changer celui-ci)
    current_path = os.path.join(base_dir, "data", "prod_batch_BIG_DRIFT.csv")

    print("CURRENT FILE USED:", current_path)

    # Output (où seront écrits reference_data.csv et current_data.csv)
    output_dir = os.path.join(base_dir, "data")

    print(f"Loading reference data from: {reference_path}")
    print(f"Loading current (prod) data from: {current_path}")

    # -----------------------------
    # LOAD CSV
    # -----------------------------
    try:
        reference_data = pd.read_csv(reference_path)
        current_data = pd.read_csv(current_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    print(f"Reference data loaded. Shape: {reference_data.shape}")
    print(f"Current data loaded. Shape: {current_data.shape}")

    # -----------------------------
    # CLEANING (important)
    # -----------------------------
    # 1) Colonnes à supprimer (inutile / ID)
    drop_cols = ["Unnamed: 21", "CLIENTNUM"]
    reference_data = reference_data.drop(columns=drop_cols, errors="ignore")
    current_data = current_data.drop(columns=drop_cols, errors="ignore")

    # 2) (Optionnel) Nettoyer les espaces dans les catégories (évite faux drift)
    cat_cols = ["Gender", "Education_Level", "Marital_Status", "Income_Category", "Card_Category", "Attrition_Flag"]
    for c in cat_cols:
        if c in reference_data.columns:
            reference_data[c] = reference_data[c].astype(str).str.strip()
        if c in current_data.columns:
            current_data[c] = current_data[c].astype(str).str.strip()

    print("Dropped useless columns:", drop_cols)
    print(f"Reference shape after cleaning: {reference_data.shape}")
    print(f"Current shape after cleaning: {current_data.shape}")

    # -----------------------------
    # (Optionnel) Vérifier que les colonnes matchent
    # -----------------------------
    ref_cols = set(reference_data.columns)
    cur_cols = set(current_data.columns)
    only_in_ref = sorted(list(ref_cols - cur_cols))
    only_in_cur = sorted(list(cur_cols - ref_cols))

    if only_in_ref or only_in_cur:
        print("⚠️ Column mismatch detected!")
        if only_in_ref:
            print("Columns only in reference:", only_in_ref)
        if only_in_cur:
            print("Columns only in current:", only_in_cur)
        # On continue quand même, mais idéalement il faut corriger

    # -----------------------------
    # SAVE FILES
    # -----------------------------
    os.makedirs(output_dir, exist_ok=True)

    ref_out = os.path.join(output_dir, "reference_data.csv")
    cur_out = os.path.join(output_dir, "current_data.csv")

    reference_data.to_csv(ref_out, index=False)
    current_data.to_csv(cur_out, index=False)

    print(f"Saved reference data to: {ref_out}")
    print(f"Saved current data to: {cur_out}")

if __name__ == "__main__":
    prepare_data()
    print("✅ prepare_data finished.")
    print("🚀 Launching score_data.py automatically...")

    try:
        subprocess.run(
            [sys.executable, "score_data.py"],
            check=True
        )
        print("✅ score_data.py completed successfully.")
    except subprocess.CalledProcessError as e:
        print("❌ Error while running score_data.py")
        print(e)

