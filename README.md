# 🏦 Bank Churn Prediction - MLOps End-to-End Project

[![MLOps](https://img.shields.io/badge/MLOps-Automated-blue)]()
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)]()
[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939)]()
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2)]()
[![Evidently](https://img.shields.io/badge/Evidently-Monitoring-FF6B6B)]()
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB)]()

> **Master 2 Data Science - Université Claude Bernard Lyon 1**  
> Un pipeline MLOps complet pour la prédiction du churn bancaire

---

## 📋 Table des Matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture MLOps](#-architecture-mlops)
- [Workflow Automatisé](#-workflow-automatisé)
- [Performances du Modèle](#-performances-du-modèle)
- [Installation & Démarrage](#-installation--démarrage)
- [Structure du Projet](#-structure-du-projet)
- [Notebooks](#-notebooks)
- [Technologies Utilisées](#-technologies-utilisées)
- [Monitoring et Drift Detection](#-monitoring-et-drift-detection)
- [Perspectives Futures](#-perspectives-futures)
- [Équipe](#-équipe)

---

## 🎯 Vue d'ensemble

Ce projet implémente un **système complet de prédiction du churn bancaire** avec un pipeline MLOps end-to-end. Il démontre l'application des meilleures pratiques MLOps incluant:

- **Expérimentation ML** avec tracking via MLflow sur DagsHub
- **Pipeline CI/CD automatisé** avec Jenkins et GitHub Webhooks
- **Monitoring de drift** avec Evidently AI
- **Déploiement containerisé** avec Docker et Docker Compose
- **API REST** avec FastAPI et interface utilisateur Streamlit

### 🎓 Contexte Académique

**Programme:** Master 2 Data Science  
**Institution:** Université Claude Bernard Lyon 1  
**Objectif pédagogique:** Maîtriser l'ensemble du cycle de vie MLOps, de l'expérimentation à la production

### 🏆 Résultats Clés

- **ROC-AUC Score:** 0.993 (modèle LightGBM optimisé)
- **F1-Score:** 0.919
- **Pipeline 100% automatisé** depuis le push Git jusqu'au déploiement
- **Monitoring en temps réel** avec détection automatique de drift

---

## 🏗️ Architecture MLOps

```
┌─────────────────────────────────────────────────────────────────┐
│                  📓 DÉVELOPPEMENT & TRACKING                     │
├─────────────────────────────────────────────────────────────────┤
│  Notebooks (3)  →  MLflow (DagsHub)  →  Model Registry         │
│  • preprocessing.ipynb                                           │
│  • modeling.ipynb     (Expérimentation)                         │
│  • mlflow_tracking.ipynb                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    🔄 VERSIONING & TRIGGER                       │
├─────────────────────────────────────────────────────────────────┤
│  GitHub Repository  →  Webhook  →  Jenkins Pipeline            │
│  (Code + Data)         (ngrok)      (Jenkinsfile)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    📊 MONITORING & VALIDATION                    │
├─────────────────────────────────────────────────────────────────┤
│  Evidently AI  →  Drift Detection  →  Reports (HTML/JSON)      │
│  (Data Quality)   (KS Test)            (Port 9000)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    🐳 BUILD & DEPLOYMENT                         │
├─────────────────────────────────────────────────────────────────┤
│  Docker Build  →  Docker Hub  →  docker-compose Deploy         │
│  (Multi-stage)    (Registry)      (3 services)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    🚀 PRODUCTION SERVICES                        │
├─────────────────────────────────────────────────────────────────┤
│  Backend (FastAPI)  |  Frontend (Streamlit)  |  Monitoring     │
│  :8000              |  :8501                 |  :9000           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow Automatisé

### 1️⃣ Phase Développement

#### **Notebooks de Développement**

Le projet est structuré en **3 notebooks Jupyter** documentant le cycle complet:

1. **`preprocessing.ipynb`** - Préparation des données
   - Nettoyage et transformation
   - Feature engineering (5 nouvelles features)
   - Gestion des valeurs manquantes
   - Encoding des variables catégorielles
   - Stratification du dataset

2. **`modeling.ipynb`** - Entraînement des modèles
   - Modèles baseline (6 algorithmes)
   - Fine-tuning avec RandomizedSearchCV
   - Ensemble learning (Stacking & Voting)
   - Évaluation comparative multi-métriques

3. **`mlflow_tracking.ipynb`** - Tracking et Registry
   - Logging de 20+ expérimentations
   - Comparaison des performances
   - Sélection du meilleur modèle
   - Enregistrement dans Model Registry

#### **MLflow sur DagsHub**

- 📊 **Tracking centralisé:** https://dagshub.com/karrayyessine1/MLOps_Project/experiments
- 🏆 **Meilleur modèle:** LightGBM (ROC-AUC: 0.9931)
- 📦 **Model Registry:** Versioning et staging des modèles
- 🔗 **Collaboration:** Partage des expérimentations entre membres de l'équipe

---

### 2️⃣ Phase CI/CD - Jenkins

#### **Configuration du Pipeline**

**Jenkins URL:** https://3fc290848417.ngrok-free.app → http://localhost:8080

Le pipeline Jenkins s'exécute automatiquement à chaque push Git via webhook:

```groovy
pipeline {
    agent any
    
    stages {
        stage('📥 Clone Repository') {
            // Clone depuis GitHub
        }
        
        stage('🐍 Setup Python Environment') {
            // Installation des dépendances
        }
        
        stage('📊 Register Best Model') {
            // Copie du modèle depuis model_registry/
        }
        
        stage('📊 Data Drift Monitoring') {
            // Evidently: détection de drift
        }
        
        stage('📄 Archive Reports') {
            // Sauvegarde rapports HTML/JSON
        }
        
        stage('📊 Publish Reports') {
            // Container nginx pour visualisation
        }
        
        stage('🐳 Build Docker Images') {
            // Build Backend + Frontend
        }
        
        stage('🚀 Push to Docker Hub') {
            // Push vers yessinekarray/*
        }
        
        stage('🚀 Deploy Application') {
            // docker-compose up
        }
        
        stage('🏥 Health Check') {
            // Validation des services
        }
    }
}
```

#### **Déclenchement Automatique**

**Configuration GitHub Webhook:**
- **URL:** `https://3fc290848417.ngrok-free.app/github-webhook/`
- **Events:** Push events
- **Content-Type:** application/json

**Flux:**
```
Nouveau push → GitHub Webhook → ngrok → Jenkins → Pipeline automatique
```

---

### 3️⃣ Phase Monitoring - Evidently AI

#### **Détection Automatique de Drift**

Le système de monitoring génère automatiquement:

- 📊 **Data Drift Report** - Distribution des features (référence vs production)
- 📈 **Performance Report** - Métriques du modèle en temps réel
- ⚠️ **Alerts** - Notifications si drift détecté
- 🌐 **Dashboard** - Rapports HTML accessibles sur http://localhost:9000

#### **Tests Automatisés**

```python
# Le monitoring détecte automatiquement le fichier le plus récent
latest_file = get_latest_prod_file("monitoring/data/")

# Tests exécutés:
✓ Data Stability Test
✓ Column Drift Test (Kolmogorov-Smirnov)
✓ Dataset Drift Test
⚠️ Alert si drift > seuil configuré
```

#### **Fichiers Surveillés**

```
monitoring/data/
├── churn2.csv              # Dataset de référence (baseline)
└── prod_batch_*.csv        # Batches de production (détection auto)
```

---

### 4️⃣ Phase Déploiement - Docker

#### **Architecture Multi-Container**

```yaml
services:
  backend:
    image: yessinekarray/churn-backend:latest
    ports: ["8000:8000"]
    volumes: ["./models:/app/processors/models"]
    
  frontend:
    image: yessinekarray/churn-frontend:latest
    ports: ["8501:8501"]
    depends_on: [backend]
    
  monitoring:
    image: monitoring-reports:latest
    ports: ["9000:80"]
```

#### **Optimisation - Modèle Externe**

**Problème:** Modèle de 1 GB → Image Docker trop lourde  
**Solution:** Modèle stocké sur host, monté via Docker volume  
**Résultat:** Images Docker ~100 MB, push/pull rapides

---

## 📊 Performances du Modèle

### **Meilleur Modèle: LightGBM (Optimisé)**

| Métrique      | Score  | Interprétation                                  |
|---------------|--------|-------------------------------------------------|
| **ROC-AUC**   | 0.9931 | Excellente discrimination des classes           |
| **F1-Score**  | 0.9192 | Équilibre optimal Precision/Recall              |
| **Precision** | 0.9023 | 90% des prédictions "Churn" sont correctes      |
| **Recall**    | 0.9372 | 94% des vrais churners sont détectés            |
| **Accuracy**  | 0.9650 | Performance globale très élevée                 |

### **Comparaison des Modèles**

Tous les modèles ont été trackés dans MLflow avec métriques complètes:

**Baseline Models:**
- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost
- LightGBM ⭐
- CatBoost

**Fine-Tuned Models:**
- Optimisation via RandomizedSearchCV (40 itérations × 5-fold CV)
- Amélioration moyenne: +2.5% ROC-AUC

**Ensemble Models:**
- Stacking Classifier (LogReg meta-learner)
- Voting Classifier (Soft voting)

---

## 🚀 Installation & Démarrage

### **Prérequis**

- Docker & Docker Compose (≥20.10)
- Git
- Python 3.9+ (pour développement local)
- Jenkins (pour CI/CD)
- ngrok (pour webhook GitHub)

### **Option 1: Déploiement Rapide (Docker)**

```bash
# 1. Cloner le repository
git clone https://github.com/YessineK/Mlops_Project.git
cd Mlops_Project

# 2. Préparer le modèle (copie depuis registry)
mkdir -p models
cp notebooks/model_registry/best_model_final.pkl models/

# 3. Lancer l'application complète
docker-compose up --build
```

**Services disponibles:**
- 🎨 **Frontend:** http://localhost:8501
- 🔌 **API Backend:** http://localhost:8000/docs (Swagger UI)
- 📊 **Monitoring:** http://localhost:9000

### **Option 2: Setup Complet avec CI/CD**

#### **1. Installation Jenkins**

```bash
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins jenkins/jenkins:lts

# Récupérer le mot de passe initial
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

#### **2. Configuration Jenkins**

1. Accéder à http://localhost:8080
2. Installer les plugins recommandés + **Docker Pipeline**
3. Créer un nouveau projet **Pipeline**
4. Configuration:
   - **SCM:** Git
   - **Repository URL:** https://github.com/YessineK/Mlops_Project.git
   - **Branch:** main
   - **Build Triggers:** ✅ GitHub hook trigger for GITScm polling
5. Ajouter les credentials Docker Hub:
   - ID: `docker-hub-credentials`
   - Type: Username with password

#### **3. Exposition Jenkins avec ngrok**

```bash
# Installer ngrok
brew install ngrok  # macOS
# ou télécharger depuis https://ngrok.com/download

# Exposer Jenkins
ngrok http 8080

# Note: L'URL générée (ex: https://3fc290848417.ngrok-free.app)
```

#### **4. Configuration GitHub Webhook**

1. Aller dans **Settings** → **Webhooks** → **Add webhook**
2. Configuration:
   - **Payload URL:** `https://YOUR_NGROK_URL/github-webhook/`
   - **Content type:** application/json
   - **Events:** ✅ Just the push event
   - **Active:** ✅

#### **5. Test du Pipeline**

```bash
# Faire un commit test
echo "test" >> README.md
git add .
git commit -m "test: trigger Jenkins pipeline"
git push origin main

# Jenkins devrait démarrer automatiquement
# Vérifier: https://YOUR_NGROK_URL
```

---

## 📁 Structure du Projet

```
Mlops_Project/
│
├── 📓 notebooks/                       # Développement ML
│   ├── preprocessing.ipynb             # Étape 1: Préparation données
│   ├── modeling.ipynb                  # Étape 2: Entraînement modèles
│   ├── mlflow_tracking.ipynb           # Étape 3: Tracking & Registry
│   ├── model_registry/                 # Meilleurs modèles sauvegardés
│   │   ├── best_model_final.pkl        # LightGBM (1 GB)
│   │   └── metadata.json               # Métadonnées du modèle
│   └── processors/                     # Preprocessors versionnés
│       ├── preprocessor.pkl
│       ├── feature_names.pkl
│       └── preprocessed_data.pkl
│
├── 🐍 backend/                         # API FastAPI
│   ├── src/
│   │   ├── main.py                     # Endpoints REST
│   │   └── processors/
│   │       ├── models/                 # Modèles (via volume)
│   │       └── preprocessor.pkl
│   └── Dockerfile
│
├── 🎨 frontend/                        # Interface Streamlit
│   ├── app.py                          # UI utilisateur
│   └── Dockerfile
│
├── 📊 monitoring/                      # Evidently AI
│   ├── prepare_data.py                 # Détection auto dernier fichier
│   ├── score_data.py                   # Scoring production
│   ├── run_monitoring.py               # Génération rapports
│   ├── Dockerfile                      # Container nginx
│   └── data/
│       ├── churn2.csv                  # Reference dataset
│       └── prod_batch_*.csv            # Production batches
│
├── ⚙️ Jenkins/
│   └── register_best_model.py          # Script copie modèle → backend
│
├── 📦 models/                          # Modèles pour déploiement (host)
│   └── best_model_final.pkl            # Monté via Docker volume
│
├── 🐳 docker-compose.yml               # Orchestration services
├── 📋 Jenkinsfile                      # Pipeline CI/CD
├── 📄 README.md                        # Ce fichier
├── 📄 requirements.txt                 # Dépendances Python
└── .gitignore
```

---

## 📓 Notebooks

### **1. preprocessing.ipynb**

**Objectif:** Préparation et nettoyage des données

**Étapes principales:**
- Import et exploration des données (`churn2.csv`)
- Nettoyage:
  - Suppression colonnes vides
  - Conversion types (categorical encoding)
  - Gestion valeurs manquantes ("Unknown" → imputation)
- Feature Engineering:
  - `tenure_per_age`
  - `utilisation_per_age`
  - `credit_lim_per_age`
  - `total_trans_amt_per_credit_lim`
  - `total_trans_ct_per_credit_lim`
- Preprocessing pipeline:
  - StandardScaler pour variables numériques
  - OneHotEncoder pour variables catégorielles
- Sauvegarde artifacts:
  - `preprocessor.pkl`
  - `feature_names.pkl`
  - `preprocessed_data.pkl`

**Sorties:**
- Dataset preprocessé prêt pour modeling
- 28 features finales (23 originales + 5 engineerées)
- Train/Test split stratifié (80/20)

---

### **2. modeling.ipynb**

**Objectif:** Entraînement, optimisation et sélection du meilleur modèle

**Étapes principales:**

1. **Baseline Models** (6 modèles):
   ```python
   - Logistic Regression
   - Random Forest
   - Gradient Boosting
   - XGBoost
   - LightGBM
   - CatBoost
   ```

2. **Fine-Tuning** (RandomizedSearchCV):
   - 40 itérations × 5-fold CV
   - Optimisation sur PR-AUC (métrique clé churn)
   - Recherche d'hyperparamètres:
     - Learning rate: [0.01, 0.02, 0.03, 0.05]
     - N_estimators: [400, 600, 800, 1000]
     - Max_depth, min_samples, etc.

3. **Ensemble Learning**:
   - Stacking Classifier (LogReg meta-learner)
   - Voting Classifier (Soft voting)

4. **Évaluation Multi-Métriques**:
   - Accuracy, Precision, Recall
   - F1-Score, ROC-AUC, PR-AUC
   - Courbes ROC et Precision-Recall
   - Matrices de confusion

5. **Sauvegarde du Meilleur Modèle**:
   - Score composite pondéré:
     - ROC-AUC: 35%
     - F1-Score: 30%
     - Recall: 25%
     - Precision: 10%

**Sorties:**
- `best_model_final.pkl` (LightGBM optimisé)
- `model_comparison_final.csv`
- `model_improvements.csv`
- Graphiques de comparaison

---

### **3. mlflow_tracking.ipynb**

**Objectif:** Tracking MLflow et gestion du Model Registry

**Étapes principales:**

1. **Configuration MLflow + DagsHub**:
   ```python
   MLFLOW_TRACKING_URI = "https://dagshub.com/karrayyessine1/MLOps_Project.mlflow"
   EXPERIMENT_NAME = "churn_prediction"
   ```

2. **Logging des Modèles**:
   - Production model (1 run)
   - Tuned models (6 runs)
   - Ensemble models (2 runs)
   - **Total: 9 runs trackées**

3. **Métadonnées Loggées**:
   - Paramètres (hyperparamètres, dataset)
   - Métriques (accuracy, F1, ROC-AUC, etc.)
   - Artifacts (modèles .pkl)
   - Durée d'entraînement

4. **Model Registry Local**:
   ```
   model_registry/
   ├── Best_Churn_LightGBM/
   │   ├── 1.0.0/
   │   │   ├── model.pkl
   │   │   └── metadata.json
   │   └── production.pkl
   ```

5. **Lecture et Comparaison**:
   - Pandas DataFrame depuis MLflow
   - Tri par ROC-AUC
   - Sélection du meilleur modèle

**Sorties:**
- Dashboard MLflow complet sur DagsHub
- Model Registry versionné
- Meilleur modèle prêt pour déploiement

**Accès Dashboard:**
- https://dagshub.com/karrayyessine1/MLOps_Project/experiments

---

## 🔧 Technologies Utilisées

### **Machine Learning**

| Technologie | Usage | Version |
|-------------|-------|---------|
| **scikit-learn** | Preprocessing, baseline models | 1.3+ |
| **LightGBM** | Meilleur modèle (Gradient Boosting) | 4.0+ |
| **XGBoost** | Alternative Gradient Boosting | 2.0+ |
| **CatBoost** | Handling de features catégorielles | 1.2+ |
| **imbalanced-learn** | SMOTE (gestion déséquilibre) | 0.11+ |
| **pandas** | Manipulation de données | 2.0+ |
| **numpy** | Calculs numériques | 1.24+ |

### **MLOps & Tracking**

| Technologie | Usage | Version |
|-------------|-------|---------|
| **MLflow** | Experiment tracking, model registry | 2.8+ |
| **DagsHub** | Remote MLflow server (collaboration) | - |
| **Evidently AI** | Data drift detection, monitoring | 0.4+ |

### **CI/CD & Deployment**

| Technologie | Usage | Version |
|-------------|-------|---------|
| **Jenkins** | Pipeline automation (CI/CD) | 2.426+ |
| **Docker** | Containerization | 24.0+ |
| **Docker Compose** | Multi-container orchestration | 2.23+ |
| **Docker Hub** | Image registry | - |
| **GitHub Webhooks** | Auto-trigger Jenkins on push | - |
| **ngrok** | Expose Jenkins for webhook | 3.0+ |

### **Backend & Frontend**

| Technologie | Usage | Version |
|-------------|-------|---------|
| **FastAPI** | RESTful API (Python) | 0.104+ |
| **Streamlit** | Interactive web UI | 1.28+ |
| **uvicorn** | ASGI server | 0.24+ |
| **Pydantic** | Data validation | 2.5+ |

### **Monitoring & Reporting**

| Technologie | Usage | Version |
|-------------|-------|---------|
| **nginx** | Servir rapports HTML | 1.25+ |
| **matplotlib** | Visualisations statiques | 3.7+ |
| **seaborn** | Visualisations statistiques | 0.12+ |

---

## 📊 Monitoring et Drift Detection

### **Architecture de Monitoring**

```python
monitoring/
├── prepare_data.py          # Détection auto dernier batch
├── score_data.py            # Scoring avec modèle de production
├── run_monitoring.py        # Génération rapports Evidently
└── data/
    ├── churn2.csv           # Reference dataset (baseline)
    └── prod_batch_*.csv     # Production batches
```

### **Rapports Générés**

#### **1. Data Drift Report**
- Comparaison distributions (reference vs current)
- Tests statistiques par feature (Kolmogorov-Smirnov)
- Visualisation des drifts détectés

#### **2. Performance Report**
- Métriques du modèle en production
- Comparaison avec baseline
- Dégradation de performance

#### **3. Test Results (JSON)**
```json
{
  "data_stability": "PASS",
  "column_drift": "WARNING",
  "dataset_drift": "FAIL",
  "drifted_features": ["total_trans_ct", "avg_utilization_ratio"]
}
```

### **Accès aux Rapports**

**Dashboard:** http://localhost:9000

Contenu:
- `monitoring_report.html` - Visualisation interactive du drift
- `performance_report.html` - Métriques de performance
- `*.json` - Résultats des tests automatisés

### **Alerting (Future)**

Si drift détecté (seuil > 3 features):
1. 📧 Email aux data scientists
2. 📱 Notification Slack
3. 🔄 Déclenchement auto-retraining (roadmap)

---

## 🔮 Perspectives Futures

### **Phase 1: Auto-Retraining** 🤖

**Workflow proposé:**
```
Drift détecté (> seuil)
    ↓
Combine old data + new batch
    ↓
Train nouveau modèle
    ↓
Validation (compare performances vs modèle actuel)
    ↓
Si meilleur → Deploy automatique
Sinon       → Alerte équipe
```

**Implémentation:**
- Nouveau stage Jenkins: "Auto-Retraining if Drift"
- Scripts: `retrain_with_new_data.py`, `validate_new_model.py`
- Seuil configurable: 3+ colonnes en drift

---

### **Phase 2: Model Storage Scalable** ☁️

**Problème actuel:** Modèle 1GB monté via volume Docker

**Solution proposée:**
- **MinIO** (S3-compatible, self-hosted)
- Backend télécharge modèle au démarrage
- Versioning avec tags (v1.0, v1.1, etc.)
- Rollback rapide en cas de problème

**Architecture:**
```
MinIO (S3)
├── models/
│   ├── churn_v1.0.pkl
│   ├── churn_v1.1.pkl
│   └── churn_latest.pkl
```

### **Phase 3: A/B Testing** 🧪

**Objectif:** Comparer 2 versions du modèle en production

**Implémentation:**
```python
# Traffic routing
if user_id % 2 == 0:
    model = load_model("v1.0")  # 50% traffic
else:
    model = load_model("v1.1")  # 50% traffic

# Tracking des performances
log_prediction(user_id, model_version, prediction, actual)
```

**Métriques comparées:**
- ROC-AUC en production
- Latence moyenne
- Taux de faux positifs/négatifs
- Feedback utilisateur

---

### **Phase 5: Real-Time Monitoring Dashboard** 📊

**Stack proposé:**
- **Grafana:** Visualisation temps réel
- **Prometheus:** Collecte métriques
- **Alerting:** Slack/Email

**Métriques trackées:**
```
- Nombre de prédictions/min
- Latence P50/P95/P99
- Taux de drift par feature
- Distribution des prédictions
- Taux d'erreur API
- Utilisation CPU/Mémoire
```

**Alertes configurées:**
- Drift détecté sur >3 features
- Latence >500ms
- Taux d'erreur >1%
- Dégradation ROC-AUC >5%

---


### **Dashboard Monitoring**

**URL:** http://localhost:9000

**Rapports disponibles:**

1. **monitoring_report.html**
   - Data Drift Analysis
   - Distribution plots (reference vs current)
   - Statistical tests results

2. **performance_report.html**
   - Model performance metrics
   - Confusion matrix
   - ROC curve & PR curve

3. **drift_tests.json**
   - Test results détaillés
   - Features en drift
   - Timestamps

---

### **MLflow Tracking**

**Dashboard:** https://dagshub.com/karrayyessine1/MLOps_Project/experiments

**Fonctionnalités:**
- 📊 Compare runs (métriques, paramètres)
- 📈 Visualisation courbes de learning
- 📦 Download artifacts (modèles, plots)
- 🏷️ Tagging et notes sur runs
- 🔍 Search & filter experiments

---

### **Master 2 Data Science - Université Claude Bernard Lyon 1**

Ce projet a été réalisé dans le cadre du Master 2 Data Science à l'**Université Claude Bernard Lyon 1** (UCBL).

#### **Contributions principales:**

- **Architecture MLOps:** Design du pipeline end-to-end
- **Développement Notebooks:** Preprocessing, Modeling, MLflow Tracking
- **Configuration CI/CD:** Jenkins, Docker, GitHub Webhooks
- **Monitoring:** Implémentation Evidently AI
- **Déploiement:** Docker Compose, services production

#### **Encadrement académique:**

- **Programme:** Master 2 Data Science
- **Institution:** Université Claude Bernard Lyon 1
- **Année:** 2025-2026

---


