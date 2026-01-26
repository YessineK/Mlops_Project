"""
Deepchecks Validation - Version Simple et Fonctionnelle
"""
import os
import sys
import pandas as pd
import joblib
from datetime import datetime

print("="*80)
print("🚀 DEEPCHECKS VALIDATION - DÉMARRAGE")
print("="*80)

try:
    from deepchecks.tabular import Dataset
    from deepchecks.tabular.suites import (
        data_integrity,
        train_test_validation, 
        model_evaluation
    )
    print("✅ Deepchecks importé avec succès")
except Exception as e:
    print(f"❌ Erreur import Deepchecks: {e}")
    print("💡 Installez: pip install setuptools deepchecks")
    sys.exit(0)


def main():
    # Chemins
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    
    model_path = os.path.join(project_root, "backend/src/processors/models/best_model_final.pkl")
    data_path = os.path.join(project_root, "monitoring/data/churn2.csv")
    
    print(f"\n📂 Chemins:")
    print(f"   Model: {model_path}")
    print(f"   Data: {data_path}")
    
    # Vérifier que les fichiers existent
    if not os.path.exists(model_path):
        print(f"\n❌ Modèle introuvable: {model_path}")
        create_error_report(base_dir, "Modèle introuvable")
        sys.exit(0)
    
    if not os.path.exists(data_path):
        print(f"\n❌ Données introuvables: {data_path}")
        create_error_report(base_dir, "Données introuvables")
        sys.exit(0)
    
    # Charger le modèle
    print("\n📥 Chargement du modèle...")
    try:
        model = joblib.load(model_path)
        print("✅ Modèle chargé")
    except Exception as e:
        print(f"❌ Erreur chargement modèle: {e}")
        create_error_report(base_dir, f"Erreur chargement modèle: {e}")
        sys.exit(0)
    
    # Charger les données
    print("\n📥 Chargement des données...")
    try:
        df = pd.read_csv(data_path)
        print(f"✅ Données chargées: {df.shape}")
    except Exception as e:
        print(f"❌ Erreur chargement données: {e}")
        create_error_report(base_dir, f"Erreur chargement données: {e}")
        sys.exit(0)
    
    # Nettoyer les données
    print("\n🧹 Nettoyage des données...")
    df.drop(columns=["CLIENTNUM", "Unnamed: 21"], errors="ignore", inplace=True)
    
    # Créer la target
    if "Attrition_Flag" in df.columns:
        df["target"] = (df["Attrition_Flag"] == "Attrited Customer").astype(int)
        df.drop(columns=["Attrition_Flag"], inplace=True)
        print("✅ Target créée")
    else:
        print("❌ Colonne Attrition_Flag introuvable")
        create_error_report(base_dir, "Colonne target manquante")
        sys.exit(0)
    
    # Split train/test
    print("\n✂️ Split train/test...")
    from sklearn.model_selection import train_test_split
    
    train_df, test_df = train_test_split(
        df, 
        test_size=0.2, 
        stratify=df["target"],
        random_state=42
    )
    print(f"✅ Train: {train_df.shape}, Test: {test_df.shape}")
    
    # Créer les datasets Deepchecks
    print("\n📊 Création des datasets Deepchecks...")
    cat_features = train_df.select_dtypes(include=["object", "category"]).columns.tolist()
    if "target" in cat_features:
        cat_features.remove("target")
    
    train_dataset = Dataset(train_df, label="target", cat_features=cat_features)
    test_dataset = Dataset(test_df, label="target", cat_features=cat_features)
    print(f"✅ Datasets créés (categorical: {len(cat_features)} features)")
    
    # SUITE 1: Data Integrity
    print("\n" + "="*80)
    print("1️⃣ DATA INTEGRITY SUITE")
    print("="*80)
    try:
        suite = data_integrity()
        result = suite.run(train_dataset)
        
        html_path = os.path.join(base_dir, "data_integrity_report.html")
        result.save_as_html(html_path)
        
        passed = result.passed()
        print(f"{'✅ PASSED' if passed else '⚠️ FAILED'}")
        print(f"📄 Rapport: {html_path}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # SUITE 2: Train-Test Validation
    print("\n" + "="*80)
    print("2️⃣ TRAIN-TEST VALIDATION SUITE")
    print("="*80)
    try:
        suite = train_test_validation()
        result = suite.run(train_dataset, test_dataset)
        
        html_path = os.path.join(base_dir, "train_test_validation_report.html")
        result.save_as_html(html_path)
        
        passed = result.passed()
        print(f"{'✅ PASSED' if passed else '⚠️ FAILED'}")
        print(f"📄 Rapport: {html_path}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # SUITE 3: Model Evaluation
    print("\n" + "="*80)
    print("3️⃣ MODEL EVALUATION SUITE")
    print("="*80)
    try:
        suite = model_evaluation()
        result = suite.run(train_dataset, test_dataset, model)
        
        html_path = os.path.join(base_dir, "model_evaluation_report.html")
        result.save_as_html(html_path)
        
        passed = result.passed()
        print(f"{'✅ PASSED' if passed else '⚠️ FAILED'}")
        print(f"📄 Rapport: {html_path}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Créer le résumé
    print("\n📋 Création du résumé...")
    create_summary(base_dir)
    
    print("\n" + "="*80)
    print("✅ DEEPCHECKS TERMINÉ")
    print("="*80)
    print(f"📂 Rapports générés dans: {base_dir}")
    print("")
    
    # Liste les fichiers générés
    html_files = [f for f in os.listdir(base_dir) if f.endswith('.html')]
    if html_files:
        print("📄 Fichiers HTML générés:")
        for f in html_files:
            print(f"   - {f}")
    
    sys.exit(0)


def create_summary(base_dir):
    """Créer un résumé HTML simple"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Vérifier quels rapports existent
    reports = {
        "data_integrity_report.html": "Data Integrity",
        "train_test_validation_report.html": "Train-Test Validation",
        "model_evaluation_report.html": "Model Evaluation"
    }
    
    report_links = []
    for filename, title in reports.items():
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            report_links.append(f'<li><a href="{filename}">{title}</a> ✅</li>')
        else:
            report_links.append(f'<li>{title} ❌ (non généré)</li>')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Deepchecks Summary</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            background: #0b0f17;
            color: #e8eefc;
            padding: 20px;
        }}
        h1 {{ color: #1db954; }}
        .timestamp {{ color: #9fb0d0; margin-bottom: 30px; }}
        ul {{
            list-style: none;
            padding: 0;
        }}
        li {{
            margin: 15px 0;
            padding: 15px;
            background: #121a27;
            border-radius: 8px;
        }}
        a {{
            color: #1db954;
            text-decoration: none;
            font-size: 18px;
        }}
        a:hover {{ color: #1ed760; }}
    </style>
</head>
<body>
    <h1>🔍 Deepchecks Validation Summary</h1>
    <div class="timestamp">Generated: {timestamp}</div>
    
    <h2>📄 Available Reports</h2>
    <ul>
        {''.join(report_links)}
    </ul>
</body>
</html>
"""
    
    summary_path = os.path.join(base_dir, "deepchecks_summary.html")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Résumé créé: {summary_path}")


def create_error_report(base_dir, error_msg):
    """Créer un rapport d'erreur"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Deepchecks Error</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            background: #0b0f17;
            color: #e8eefc;
            padding: 20px;
        }}
        .error {{
            background: #ff4d4d;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>❌ Deepchecks Error</h1>
    <p>Generated: {timestamp}</p>
    
    <div class="error">
        <h2>Error:</h2>
        <p>{error_msg}</p>
    </div>
    
    <p>Veuillez vérifier les logs Jenkins pour plus de détails.</p>
</body>
</html>
"""
    
    error_path = os.path.join(base_dir, "deepchecks_summary.html")
    with open(error_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Rapport d'erreur créé: {error_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        create_error_report(base_dir, str(e))
        
        sys.exit(0)   