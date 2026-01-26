"""
Deepchecks Validation - Version Simplifiée
Génère un rapport unique et clair pour validation du modèle
"""
import os
import sys
import pandas as pd
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split

# Deepchecks imports
from deepchecks.tabular import Dataset
from deepchecks.tabular.suites import full_suite


def load_data_and_model():
    """Charger les données et le modèle"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    
    # Paths
    model_path = os.path.join(project_root, "backend/src/processors/models/best_model_final.pkl")
    data_path = os.path.join(project_root, "monitoring/data/churn2.csv")
    
    print(f"📂 Loading model: {model_path}")
    print(f"📂 Loading data: {data_path}")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Model not found: {model_path}")
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"❌ Data not found: {data_path}")
    
    # Load
    model = joblib.load(model_path)
    df = pd.read_csv(data_path)
    
    print(f"✅ Model loaded")
    print(f"✅ Data loaded: {df.shape}")
    
    return model, df


def prepare_data(df):
    """Nettoyer et préparer les données"""
    
    # Supprimer colonnes inutiles
    df = df.drop(columns=["CLIENTNUM", "Unnamed: 21"], errors="ignore")
    
    # Créer target binaire
    if "Attrition_Flag" in df.columns:
        df["churn"] = (df["Attrition_Flag"] == "Attrited Customer").astype(int)
        df = df.drop(columns=["Attrition_Flag"])
    
    print(f"✅ Data cleaned: {df.shape}")
    print(f"   Target distribution: {df['churn'].value_counts().to_dict()}")
    
    return df


def create_datasets(df):
    """Créer train/test datasets pour Deepchecks"""
    
    # Split
    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=42,
        stratify=df["churn"]
    )
    
    print(f"✅ Train/Test split:")
    print(f"   Train: {train_df.shape}")
    print(f"   Test: {test_df.shape}")
    
    # Identifier features catégorielles
    cat_features = train_df.select_dtypes(include=["object", "category"]).columns.tolist()
    if "churn" in cat_features:
        cat_features.remove("churn")
    
    print(f"📊 Categorical features: {cat_features}")
    
    # Créer Deepchecks Datasets
    train_dataset = Dataset(
        train_df,
        label="churn",
        cat_features=cat_features
    )
    
    test_dataset = Dataset(
        test_df,
        label="churn",
        cat_features=cat_features
    )
    
    return train_dataset, test_dataset


def run_full_validation(train_dataset, test_dataset, model, output_dir):
    """Exécuter la suite complète de validation Deepchecks"""
    
    print("")
    print("="*80)
    print("🔍 DEEPCHECKS FULL VALIDATION SUITE")
    print("="*80)
    
    try:
        # Full suite (data integrity + train-test + model evaluation)
        suite = full_suite()
        
        print("🔍 Running validation tests...")
        result = suite.run(
            train_dataset=train_dataset,
            test_dataset=test_dataset,
            model=model
        )
        
        # Sauvegarder le rapport HTML
        report_path = os.path.join(output_dir, "deepchecks_report.html")
        result.save_as_html(report_path)
        
        print(f"✅ Rapport sauvegardé: {report_path}")
        
        # Analyser les résultats
        total_checks = len(result.results)
        passed_checks = sum(1 for r in result.results if r.passed_conditions())
        failed_checks = total_checks - passed_checks
        
        print("")
        print("="*80)
        print("📊 RÉSULTATS DE VALIDATION")
        print("="*80)
        print(f"Total checks: {total_checks}")
        print(f"✅ Passed: {passed_checks}")
        print(f"❌ Failed: {failed_checks}")
        
        if failed_checks > 0:
            print("")
            print(f"⚠️  {failed_checks} checks ont échoué")
            print("   📊 Consultez le rapport pour plus de détails")
        else:
            print("")
            print("✅ Tous les checks sont passés!")
        
        print("="*80)
        
        return {
            "report_path": report_path,
            "total": total_checks,
            "passed": passed_checks,
            "failed": failed_checks,
            "success": failed_checks == 0
        }
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de Deepchecks: {e}")
        import traceback
        traceback.print_exc()
        raise


def generate_error_report(error_message, output_dir):
    """Générer un rapport d'erreur en cas de crash"""
    
    import traceback
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Deepchecks - Error Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            background: #0b0f17;
            color: #e8eefc;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #ff4d4d 0%, #c62828 100%);
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            color: white;
            font-size: 32px;
        }}
        .timestamp {{
            color: rgba(255,255,255,0.8);
            margin-top: 10px;
            font-size: 14px;
        }}
        .error-box {{
            background: #121a27;
            border: 2px solid #ff4d4d;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .error-box h2 {{
            color: #ff4d4d;
            margin-top: 0;
        }}
        pre {{
            background: #0a0e15;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            color: #9fb0d0;
            font-size: 12px;
            line-height: 1.5;
        }}
        .note {{
            background: rgba(255, 208, 0, 0.1);
            border-left: 4px solid #ffd000;
            padding: 15px;
            border-radius: 8px;
            color: #ffd000;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>❌ Deepchecks Validation Error</h1>
        <div class="timestamp">Generated: {timestamp}</div>
    </div>
    
    <div class="error-box">
        <h2>Error Message</h2>
        <pre>{error_message}</pre>
    </div>
    
    <div class="error-box">
        <h2>Full Traceback</h2>
        <pre>{traceback.format_exc()}</pre>
    </div>
    
    <div class="note">
        <strong>⚠️ Note:</strong> Cette erreur n'a pas bloqué le pipeline MLOps.
        Le déploiement continue normalement. Vérifiez les logs Jenkins pour plus de détails.
    </div>
</body>
</html>
"""
    
    report_path = os.path.join(output_dir, "deepchecks_report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ Error report saved: {report_path}")
    return report_path


def main():
    """Main execution"""
    
    print("="*80)
    print("🚀 DEEPCHECKS VALIDATION")
    print("="*80)
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # 1. Charger données et modèle
        model, df = load_data_and_model()
        
        # 2. Préparer les données
        df = prepare_data(df)
        
        # 3. Créer train/test datasets
        train_dataset, test_dataset = create_datasets(df)
        
        # 4. Exécuter validation complète
        results = run_full_validation(train_dataset, test_dataset, model, output_dir)
        
        # 5. Retour basé sur les résultats
        if results["failed"] == 0:
            print("")
            print("✅ VALIDATION COMPLÈTE: SUCCÈS")
            sys.exit(0)
        else:
            print("")
            print("⚠️  VALIDATION COMPLÈTE: WARNINGS")
            print("   Le rapport contient des recommandations")
            sys.exit(0)  # Ne bloque PAS le pipeline
        
    except Exception as e:
        print("")
        print("="*80)
        print(f"❌ ERREUR CRITIQUE: {e}")
        print("="*80)
        
        # Générer rapport d'erreur
        generate_error_report(str(e), output_dir)
        
        print("")
        print("⚠️  Une erreur s'est produite, mais le pipeline continue")
        sys.exit(0)  # Ne bloque PAS le pipeline


if __name__ == "__main__":
    main()