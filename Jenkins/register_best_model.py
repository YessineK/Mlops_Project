#!/usr/bin/env python3
"""
Script Jenkins : Charge le meilleur modèle depuis le registry local
et copie tous les fichiers nécessaires vers backend/src/
"""

import os
import sys
import pickle
import json
import shutil
from pathlib import Path

# Chemins du projet
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_REGISTRY_DIR = PROJECT_ROOT / "notebooks" / "model_registry"
NOTEBOOKS_PROCESSORS = PROJECT_ROOT / "notebooks" / "processors"
BACKEND_PROCESSORS = PROJECT_ROOT / "backend" / "src" / "processors"
BACKEND_MODEL_DIR = BACKEND_PROCESSORS / "models"

def create_directories():
    """Créer les dossiers nécessaires"""
    BACKEND_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    BACKEND_PROCESSORS.mkdir(parents=True, exist_ok=True)
    print("✅ Dossiers créés")

def find_best_model():
    """Trouve le meilleur modèle Churn dans le registry"""
    
    print("="*80)
    print("🔍 RECHERCHE DU MEILLEUR MODÈLE DANS LE REGISTRY LOCAL")
    print("="*80)
    
    # Vérifier que le registry existe
    if not MODEL_REGISTRY_DIR.exists():
        print(f"❌ Registry non trouvé: {MODEL_REGISTRY_DIR}")
        return None
    
    print(f"✅ Registry trouvé: {MODEL_REGISTRY_DIR}")
    
    # Lister tous les modèles
    models = [d for d in MODEL_REGISTRY_DIR.iterdir() if d.is_dir()]
    
    if not models:
        print("❌ Aucun modèle trouvé dans le registry!")
        return None
    
    print(f"\n📋 Modèles disponibles:")
    for model in models:
        print(f"   • {model.name}")
    
    # Chercher le modèle Churn (priorité)
    churn_models = [m for m in models if 'Churn' in m.name and 'LightGBM' in m.name]
    
    if churn_models:
        best_model = churn_models[0]
        print(f"\n✅ Modèle Churn sélectionné: {best_model.name}")
        return best_model
    
    # Sinon prendre le premier modèle
    best_model = models[0]
    print(f"\n⚠️ Aucun modèle Churn trouvé, utilisation de: {best_model.name}")
    return best_model

def load_model_from_registry(model_dir):
    """Charge le modèle depuis le registry"""
    
    print("\n" + "="*80)
    print("📥 CHARGEMENT DU MODÈLE")
    print("="*80)
    
    # Chercher production.pkl
    production_pkl = model_dir / "production.pkl"
    
    if not production_pkl.exists():
        print(f"❌ production.pkl non trouvé dans {model_dir}")
        print(f"\n📂 Contenu du dossier:")
        for item in model_dir.iterdir():
            print(f"   • {item.name}")
        return None, None
    
    # Charger le modèle
    try:
        with open(production_pkl, 'rb') as f:
            model = pickle.load(f)
        print(f"✅ Modèle chargé depuis: {production_pkl}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return None, None
    
    # Charger les métadonnées
    metadata = {}
    versions = [d for d in model_dir.iterdir() if d.is_dir()]
    
    if versions:
        latest_version = sorted(versions)[-1]
        metadata_path = latest_version / "metadata.json"
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                print("\n📊 INFORMATIONS DU MODÈLE:")
                print(f"   Nom:       {metadata.get('model_name', 'N/A')}")
                print(f"   Type:      {metadata.get('model_type', 'N/A')}")
                print(f"   ROC-AUC:   {metadata.get('metrics', {}).get('roc_auc', 0):.4f}")
                print(f"   F1-Score:  {metadata.get('metrics', {}).get('f1_score', 0):.4f}")
                print(f"   Precision: {metadata.get('metrics', {}).get('precision', 0):.4f}")
                print(f"   Recall:    {metadata.get('metrics', {}).get('recall', 0):.4f}")
                
            except Exception as e:
                print(f"⚠️ Impossible de lire les métadonnées: {e}")
    
    return model, metadata

def copy_model_to_backend(model, metadata):
    """Copie le modèle vers backend/src/processors/models/"""
    
    print("\n" + "="*80)
    print("📦 COPIE DU MODÈLE VERS BACKEND")
    print("="*80)
    
    # Sauvegarder le modèle
    model_path = BACKEND_MODEL_DIR / "best_model_final.pkl"
    
    try:
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        file_size = model_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Modèle copié: {model_path}")
        print(f"   Taille: {file_size:.2f} MB")
    except Exception as e:
        print(f"❌ Erreur lors de la copie du modèle: {e}")
        return False
    
    # Sauvegarder les métadonnées
    metadata_path = BACKEND_MODEL_DIR / "best_model_final_metadata.pkl"
    
    try:
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"✅ Métadonnées copiées: {metadata_path}")
    except Exception as e:
        print(f"⚠️ Impossible de copier les métadonnées: {e}")
    
    return True

def copy_preprocessors():
    """Copie les fichiers preprocessors depuis notebooks vers backend"""
    
    print("\n" + "="*80)
    print("📦 COPIE DES PREPROCESSORS")
    print("="*80)
    
    if not NOTEBOOKS_PROCESSORS.exists():
        print(f"⚠️ Dossier processors non trouvé: {NOTEBOOKS_PROCESSORS}")
        return False
    
    # Fichiers à copier
    files_to_copy = [
        'preprocessor.pkl',
        'feature_names.pkl',
        'preprocessing_strategy.pkl',
        'preprocessed_data.pkl'
    ]
    
    success_count = 0
    
    for filename in files_to_copy:
        src = NOTEBOOKS_PROCESSORS / filename
        dst = BACKEND_PROCESSORS / filename
        
        if src.exists():
            try:
                shutil.copy2(src, dst)
                file_size = src.stat().st_size / (1024 * 1024)  # MB
                print(f"✅ Copié: {filename} ({file_size:.2f} MB)")
                success_count += 1
            except Exception as e:
                print(f"❌ Erreur lors de la copie de {filename}: {e}")
        else:
            print(f"⚠️ Fichier non trouvé: {filename}")
    
    print(f"\n📊 Résumé: {success_count}/{len(files_to_copy)} fichiers copiés")
    
    return success_count > 0

def verify_backend_files():
    """Vérifie que tous les fichiers critiques sont présents"""
    
    print("\n" + "="*80)
    print("🔍 VÉRIFICATION DES FICHIERS BACKEND")
    print("="*80)
    
    critical_files = [
        BACKEND_MODEL_DIR / 'best_model_final.pkl',
        BACKEND_PROCESSORS / 'preprocessor.pkl',
        BACKEND_PROCESSORS / 'feature_names.pkl'
    ]
    
    all_exist = True
    
    for filepath in critical_files:
        if filepath.exists():
            file_size = filepath.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ {filepath.name} ({file_size:.2f} MB)")
        else:
            print(f"❌ MANQUANT: {filepath.name}")
            all_exist = False
    
    return all_exist

def main():
    """Point d'entrée principal"""
    
    print("\n")
    print("="*80)
    print("🚀 JENKINS - DÉPLOIEMENT DU MODÈLE DEPUIS LE REGISTRY LOCAL")
    print("="*80)
    print(f"📂 Projet: {PROJECT_ROOT}")
    print(f"📂 Registry: {MODEL_REGISTRY_DIR}")
    print(f"📂 Backend: {BACKEND_PROCESSORS}")
    print("="*80)
    
    # 1. Créer les dossiers
    create_directories()
    
    # 2. Trouver le meilleur modèle
    model_dir = find_best_model()
    if not model_dir:
        print("\n❌ ÉCHEC: Aucun modèle trouvé")
        sys.exit(1)
    
    # 3. Charger le modèle
    model, metadata = load_model_from_registry(model_dir)
    if model is None:
        print("\n❌ ÉCHEC: Impossible de charger le modèle")
        sys.exit(1)
    
    # 4. Copier le modèle vers backend
    if not copy_model_to_backend(model, metadata):
        print("\n❌ ÉCHEC: Impossible de copier le modèle")
        sys.exit(1)
    
    # 5. Copier les preprocessors
    if not copy_preprocessors():
        print("\n⚠️ ATTENTION: Certains preprocessors n'ont pas été copiés")
    
    # 6. Vérifier que tout est OK
    if not verify_backend_files():
        print("\n❌ ÉCHEC: Fichiers critiques manquants")
        sys.exit(1)
    
    # 7. Succès !
    print("\n" + "="*80)
    print("✅ DÉPLOIEMENT RÉUSSI")
    print("="*80)
    print(f"📂 Fichiers disponibles dans: {BACKEND_PROCESSORS}")
    print("🚀 Prêt pour le build Docker!")
    print("="*80)
    
    sys.exit(0)

if __name__ == "__main__":
    main()