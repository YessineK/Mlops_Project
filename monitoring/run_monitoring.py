#!/usr/bin/env python3
"""
Script Jenkins : Monitoring avec Evidently
Détecte le data drift et génère un rapport HTML
"""

import os
import sys
import pandas as pd
import json
from pathlib import Path
from evidently import Report
from evidently.presets import DataDriftPreset, DataSummaryPreset
from evidently.legacy.test_suite import TestSuite
from evidently.legacy.test_preset import DataDriftTestPreset
from evidently.legacy.pipeline.column_mapping import ColumnMapping

# Paths
MONITORING_DIR = Path(__file__).parent
DATA_DIR = MONITORING_DIR / "data"
REF_PATH = DATA_DIR / "reference_data.csv"
CURR_PATH = DATA_DIR / "current_data.csv"

def main():
    print("="*80)
    print("📊 JENKINS - MONITORING DATA DRIFT")
    print("="*80)
    
    # Vérifier que les fichiers existent
    if not REF_PATH.exists() or not CURR_PATH.exists():
        print("❌ Fichiers manquants!")
        print(f"   Reference: {REF_PATH}")
        print(f"   Current: {CURR_PATH}")
        print("\n💡 Exécutez prepare_data.py d'abord")
        sys.exit(1)
    
    print(f"✅ Fichiers trouvés")
    print(f"   Reference: {REF_PATH}")
    print(f"   Current: {CURR_PATH}")
    
    # Charger les données
    print("\n📥 Chargement des données...")
    reference_data = pd.read_csv(REF_PATH)
    current_data = pd.read_csv(CURR_PATH)
    
    # Supprimer CLIENTNUM si présent
    for df in (reference_data, current_data):
        if 'CLIENTNUM' in df.columns:
            df.drop(columns=['CLIENTNUM'], inplace=True)
    
    print(f"   Reference shape: {reference_data.shape}")
    print(f"   Current shape: {current_data.shape}")
    
    # Générer le rapport
    print("\n📊 Génération du rapport Data Drift...")
    
    metrics = [
        DataDriftPreset(),
        DataSummaryPreset()
    ]
    
    report = Report(metrics=metrics)
    snapshot = report.run(current_data=current_data, reference_data=reference_data)
    
    report_path = MONITORING_DIR / "monitoring_report.html"
    snapshot.save_html(str(report_path))
    print(f"✅ Rapport sauvegardé: {report_path}")
    
    # Exécuter les tests
    print("\n🧪 Exécution des tests de drift...")
    
    column_mapping = ColumnMapping()
    column_mapping.target = 'Attrition_Flag'
    
    tests = TestSuite(tests=[DataDriftTestPreset()])
    tests.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping
    )
    
    # Sauvegarder les résultats
    json_path = MONITORING_DIR / "monitoring_tests.json"
    tests.save_json(str(json_path))
    print(f"✅ Tests sauvegardés: {json_path}")
    
    # Vérifier les résultats
    test_results = tests.as_dict()
    failed_tests = test_results['summary']['failed_tests']
    total_tests = test_results['summary']['total_tests']
    
    print("\n" + "="*80)
    print("📊 RÉSULTATS DES TESTS")
    print("="*80)
    print(f"Total tests: {total_tests}")
    print(f"Tests réussis: {total_tests - failed_tests}")
    print(f"Tests échoués: {failed_tests}")
    
    if failed_tests > 0:
        print("\n⚠️  DATA DRIFT DÉTECTÉ!")
        print(f"   {failed_tests}/{total_tests} tests ont échoué")
        print(f"   📊 Consultez le rapport: {report_path}")
        print("\n💡 RECOMMANDATION:")
        print("   → Réentraîner le modèle avec les nouvelles données")
        
        # Ne pas bloquer le pipeline (juste un warning)
        # Pour bloquer : sys.exit(1)
    else:
        print("\n✅ AUCUN DRIFT DÉTECTÉ")
        print("   Le modèle est toujours valide")
    
    print("="*80)
    
    sys.exit(0)

if __name__ == "__main__":
    main()