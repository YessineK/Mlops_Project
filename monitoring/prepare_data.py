import pandas as pd
import os
import subprocess
import sys
import glob

def get_latest_prod_file(data_dir):
    """
    Trouve automatiquement le fichier de données le plus récent
    (excluant reference_data.csv et current_data.csv)
    """
    # Tous les fichiers CSV dans data/
    all_csv = glob.glob(os.path.join(data_dir, "*.csv"))
    
    # Exclure les fichiers de sortie
    exclude_files = ["reference_data.csv", "current_data.csv", "churn2.csv"]
    prod_files = [
        f for f in all_csv 
        if os.path.basename(f) not in exclude_files
    ]
    
    if not prod_files:
        print("❌ Aucun fichier de production trouvé!")
        print(f"📂 Fichiers disponibles dans {data_dir}:")
        for f in all_csv:
            print(f"   - {os.path.basename(f)}")
        return None
    
    # Trier par date de modification (le plus récent d'abord)
    latest = max(prod_files, key=os.path.getmtime)
    
    print(f"📊 Fichier de production le plus récent détecté:")
    print(f"   {os.path.basename(latest)}")
    print(f"   Modifié le: {pd.Timestamp.fromtimestamp(os.path.getmtime(latest))}")
    
    return latest


def prepare_data():
    # -----------------------------
    # PATHS
    # -----------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    # Reference = dataset de base (ne change jamais)
    reference_path = os.path.join(data_dir, "churn2.csv")

    # Current = DÉTECTION AUTOMATIQUE du dernier fichier
    current_path = get_latest_prod_file(data_dir)
    
    if current_path is None:
        print("❌ Impossible de continuer sans fichier de production!")
        return

    print("\n" + "="*60)
    print("📊 FICHIERS UTILISÉS POUR LE MONITORING")
    print("="*60)
    print(f"📌 Reference: {os.path.basename(reference_path)}")
    print(f"🆕 Current:   {os.path.basename(current_path)}")
    print("="*60 + "\n")

    # -----------------------------
    # LOAD CSV
    # -----------------------------
    try:
        reference_data = pd.read_csv(reference_path)
        current_data = pd.read_csv(current_path)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return

    print(f"✅ Reference data loaded. Shape: {reference_data.shape}")
    print(f"✅ Current data loaded. Shape: {current_data.shape}")

    # -----------------------------
    # CLEANING
    # -----------------------------
    drop_cols = ["Unnamed: 21", "CLIENTNUM"]
    reference_data = reference_data.drop(columns=drop_cols, errors="ignore")
    current_data = current_data.drop(columns=drop_cols, errors="ignore")

    # Nettoyer les espaces dans les catégories
    cat_cols = ["Gender", "Education_Level", "Marital_Status", 
                "Income_Category", "Card_Category", "Attrition_Flag"]
    
    for c in cat_cols:
        if c in reference_data.columns:
            reference_data[c] = reference_data[c].astype(str).str.strip()
        if c in current_data.columns:
            current_data[c] = current_data[c].astype(str).str.strip()

    print(f"\n🧹 Nettoyage effectué")
    print(f"   Reference shape: {reference_data.shape}")
    print(f"   Current shape: {current_data.shape}")

    # -----------------------------
    # Vérifier que les colonnes matchent
    # -----------------------------
    ref_cols = set(reference_data.columns)
    cur_cols = set(current_data.columns)
    only_in_ref = sorted(list(ref_cols - cur_cols))
    only_in_cur = sorted(list(cur_cols - ref_cols))

    if only_in_ref or only_in_cur:
        print("\n⚠️ ATTENTION: Column mismatch detected!")
        if only_in_ref:
            print(f"   Colonnes uniquement dans reference: {only_in_ref}")
        if only_in_cur:
            print(f"   Colonnes uniquement dans current: {only_in_cur}")

    # -----------------------------
    # SAVE FILES
    # -----------------------------
    os.makedirs(data_dir, exist_ok=True)

    ref_out = os.path.join(data_dir, "reference_data.csv")
    cur_out = os.path.join(data_dir, "current_data.csv")

    reference_data.to_csv(ref_out, index=False)
    current_data.to_csv(cur_out, index=False)

    print(f"\n💾 Fichiers sauvegardés:")
    print(f"   Reference: {ref_out}")
    print(f"   Current:   {cur_out}")


if __name__ == "__main__":
    print("\n🚀 DÉMARRAGE DU MONITORING AUTOMATIQUE")
    print("="*60 + "\n")
    
    prepare_data()
    
    print("\n✅ prepare_data.py terminé avec succès!")
    print("\n🚀 Lancement automatique de score_data.py...")
    print("="*60 + "\n")

    try:
        subprocess.run(
            [sys.executable, "score_data.py"],
            check=True
        )
        print("\n✅ score_data.py terminé avec succès!")
    except subprocess.CalledProcessError as e:
        print("\n❌ Erreur lors de l'exécution de score_data.py")
        print(e)
        sys.exit(1)