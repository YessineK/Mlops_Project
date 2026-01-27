# 🏦 Bank Churn Prediction - MLOps End-to-End Project

[![MLOps](https://img.shields.io/badge/MLOps-Automated-blue)]()
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)]()
[![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939)]()
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2)]()
[![Evidently](https://img.shields.io/badge/Evidently-Monitoring-FF6B6B)]()

Système complet de prédiction du churn bancaire avec pipeline MLOps automatisé : tracking ML, monitoring de drift, CI/CD, et déploiement containerisé.

---

## 🎯 Objectif du Projet

Prédire le risque de départ des clients bancaires en utilisant un modèle de Machine Learning performant (ROC-AUC: **0.993**), avec un pipeline MLOps complet pour assurer la **qualité**, la **traçabilité**, et le **monitoring** du modèle en production.

---

## 🏗️ Architecture MLOps Complète
```
┌─────────────────────────────────────────────────────────────────┐
│                    DÉVELOPPEMENT & TRACKING                      │
├─────────────────────────────────────────────────────────────────┤
│  Notebooks  →  MLflow (DagsHub)  →  Model Registry             │
│  (Exploration)   (Tracking)           (Versioning)              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    VERSIONING & TRIGGER                          │
├─────────────────────────────────────────────────────────────────┤
│  GitHub Repository  →  Webhook  →  Jenkins Pipeline            │
│  (Code + Data)         (Auto)       (CI/CD)                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING & VALIDATION                       │
├─────────────────────────────────────────────────────────────────┤
│  Evidently AI  →  Drift Detection  →  Auto-Retraining (Future) │
│  (Data Quality)   (Alerts)             (If Drift > Threshold)   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BUILD & DEPLOYMENT                            │
├─────────────────────────────────────────────────────────────────┤
│  Docker Images  →  Docker Hub  →  docker-compose Deploy        │
│  (Backend+Frontend) (Registry)     (Production)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION SERVICES                           │
├─────────────────────────────────────────────────────────────────┤
│  Backend API (FastAPI)  |  Frontend (Streamlit)  |  Monitoring  │
│  :8000                  |  :8501                 |  :9000        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow MLOps Automatisé

### **1️⃣ Phase Développement : ML Experimentation & Tracking**
```python
# notebooks/ - Expérimentation des modèles
├── 01_data_exploration.ipynb      # EDA + Feature Engineering
├── 02_model_training.ipynb        # Training avec MLflow tracking
├── 03_model_evaluation.ipynb      # Comparaison des modèles
└── model_registry/                # Meilleur modèle versionné
    └── best_model_final.pkl       # LightGBM (ROC-AUC: 0.993)
```

**MLflow sur DagsHub** :
- 📊 Track de **20+ expérimentations** (hyperparamètres, métriques, artefacts)
- 🏆 Sélection automatique du meilleur modèle (ROC-AUC: 0.9931)
- 📦 Registry centralisé pour versioning des modèles
- 🔗 URL DagsHub : https://dagshub.com/YessineK/Mlops_Project

---

### **2️⃣ Phase CI/CD : Automatisation avec Jenkins**

#### **Déclenchement Automatique via Webhook**
```bash
# Workflow automatique
Nouvelle data ajoutée → Git push → GitHub Webhook → Jenkins Pipeline
```

**Configuration Webhook GitHub** :
- **Payload URL** : `https://YOUR_NGROK_URL/github-webhook/`
- **Events** : Push events
- **Résultat** : Jenkins démarre automatiquement à chaque push

#### **Pipeline Jenkins (Jenkinsfile)**
```groovy
pipeline {
    stages {
        stage('📥 Clone Repository')       # Clone du code depuis GitHub
        stage('🐍 Setup Python')           # Installation dépendances
        stage('📊 Register Best Model')    # Copie du modèle depuis registry
        stage('📊 Data Drift Monitoring')  # Evidently : détection drift
        stage('📄 Archive Reports')        # Sauvegarde rapports HTML/JSON
        stage('📊 Publish Reports')        # Docker container (port 9000)
        stage('🐳 Build Docker Images')    # Build Backend + Frontend
        stage('🚀 Push to Docker Hub')     # Push images vers registry
        stage('🚀 Deploy Application')     # docker-compose up
        stage('🏥 Health Check')           # Validation déploiement
    }
}
```

**Jenkins exécute automatiquement** :
1. ✅ Validation de la structure du projet
2. ✅ Enregistrement du modèle depuis `model_registry/`
3. ✅ Monitoring avec Evidently (drift + performance)
4. ✅ Build des images Docker (Backend FastAPI + Frontend Streamlit)
5. ✅ Push vers Docker Hub (`yessinekarray/churn-backend`, `churn-frontend`)
6. ✅ Déploiement avec `docker-compose`
7. ✅ Health checks des services

---

### **3️⃣ Phase Monitoring : Evidently AI pour Data Drift**
```python
# monitoring/ - Détection automatique de drift
├── prepare_data.py              # Préparation des datasets
├── score_data.py                # Scoring des nouvelles données
├── run_monitoring.py            # Génération rapports Evidently
└── data/
    ├── churn2.csv               # Reference dataset (baseline)
    └── prod_batch_*.csv         # Production batches (détection auto)
```

**Evidently génère automatiquement** :
- 📊 **Data Drift Report** : Distribution des features (reference vs current)
- 📈 **Performance Report** : Métriques du modèle en production
- ⚠️ **Alerts** : Si drift détecté → Jenkins notifie (logs + artifacts)
- 🌐 **Dashboard** : Rapports HTML accessibles sur `http://localhost:9000`

**Détection Automatique du Dernier Fichier** :
```python
# prepare_data.py détecte automatiquement le fichier le plus récent
def get_latest_prod_file(data_dir):
    prod_files = glob.glob(os.path.join(data_dir, "prod_batch_*.csv"))
    latest = max(prod_files, key=os.path.getmtime)  # Tri par date
    return latest
```

**Tests de Drift** :
- ✅ Data Stability Test
- ✅ Column Drift Test (Kolmogorov-Smirnov)
- ✅ Dataset Drift Test
- ⚠️ Si **drift > seuil** → Future : Auto-retraining

---

### **4️⃣ Phase Déploiement : Containerisation Docker**

#### **Architecture Multi-Container**
```yaml
# docker-compose.yml
services:
  backend:                          # API FastAPI
    image: yessinekarray/churn-backend:latest
    ports: ["8000:8000"]
    volumes: ["./models:/app/processors/models"]  # Modèle externe (1 GB)
    
  frontend:                         # Interface Streamlit
    image: yessinekarray/churn-frontend:latest
    ports: ["8501:8501"]
    depends_on: [backend]
    
  monitoring:                       # Rapports Evidently
    image: monitoring-reports:latest
    ports: ["9000:80"]
```

**Optimisation : Modèle Externe (Docker Volume)** :
- ❌ **Problème** : Modèle de 1 GB → Image Docker trop lourde
- ✅ **Solution** : Modèle stocké sur host, monté via volume
- 🚀 **Résultat** : Images Docker légères (~100 MB), push/pull rapides

---

## 📊 Performances du Modèle

### **Meilleur Modèle : LightGBM (Hyperparameter Tuning)**

| Métrique      | Score  | Détails                                    |
|---------------|--------|--------------------------------------------|
| **ROC-AUC**   | 0.9931 | Excellente discrimination des classes      |
| **F1-Score**  | 0.9192 | Bon équilibre Precision/Recall             |
| **Precision** | 0.9023 | 90% des prédictions "Churn" sont correctes |
| **Recall**    | 0.9372 | 94% des vrais "Churn" détectés             |

**Modèles Comparés** (trackés sur MLflow) :
- Logistic Regression (baseline)
- Random Forest
- XGBoost
- **LightGBM** ⭐ (meilleur)

---

## 🚀 Installation & Démarrage

### **Prérequis**
- Docker & Docker Compose
- Git
- Jenkins (pour CI/CD)
- ngrok (pour webhook GitHub)

### **1. Cloner le Repository**
```bash
git clone https://github.com/YessineK/Mlops_Project.git
cd Mlops_Project
```

### **2. Configuration Jenkins**

**Installer Jenkins** :
```bash
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins jenkins/jenkins:lts
```

**Configurer le Pipeline** :
1. Créer un projet Pipeline dans Jenkins
2. SCM : Git → `https://github.com/YessineK/Mlops_Project.git`
3. Build Triggers : ✅ "GitHub hook trigger for GITScm polling"
4. Credentials Docker Hub : `docker-hub-credentials`

**Exposer Jenkins avec ngrok** :
```bash
ngrok http 8080
# Copier l'URL : https://YOUR_ID.ngrok-free.app
```

**Configurer Webhook GitHub** :
- Repository Settings → Webhooks → Add webhook
- Payload URL : `https://YOUR_ID.ngrok-free.app/github-webhook/`
- Content type : `application/json`
- Events : ✅ Just the push event

### **3. Déploiement Local (Sans Jenkins)**
```bash
# Préparer le modèle
mkdir -p models
cp notebooks/model_registry/best_model_final.pkl models/

# Lancer l'application
docker-compose up --build
```

**Services Accessibles** :
- 🎨 **Frontend** : http://localhost:8501 (Interface utilisateur)
- 🔌 **Backend API** : http://localhost:8000/docs (Swagger UI)
- 📊 **Monitoring** : http://localhost:9000 (Rapports Evidently)

---

## 📁 Structure du Projet
```
Mlops_Project/
│
├── backend/src/                    # API FastAPI
│   ├── main.py                     # Endpoints API (/predict, /health)
│   ├── processors/
│   │   ├── models/                 # Modèles ML (via volume)
│   │   └── preprocessor.pkl        # Pipeline preprocessing
│   └── Dockerfile
│
├── frontend/                       # Interface Streamlit
│   ├── app.py                      # UI utilisateur
│   └── Dockerfile
│
├── notebooks/                      # ML Experimentation
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb     # MLflow tracking
│   ├── 03_model_evaluation.ipynb
│   ├── model_registry/
│   │   └── best_model_final.pkl    # Meilleur modèle (1 GB)
│   └── processors/                 # Preprocessors versionnés
│
├── monitoring/                     # Evidently AI Monitoring
│   ├── prepare_data.py             # Détection auto dernier fichier
│   ├── score_data.py               # Scoring production
│   ├── run_monitoring.py           # Génération rapports
│   ├── Dockerfile                  # Container monitoring (nginx)
│   └── data/
│       ├── churn2.csv              # Reference dataset
│       └── prod_batch_*.csv        # Production batches
│
├── Jenkins/
│   └── register_best_model.py      # Copie modèle → backend/
│
├── models/                         # Modèles pour déploiement (host)
│   └── best_model_final.pkl        # Monté via Docker volume
│
├── docker-compose.yml              # Orchestration multi-container
├── Jenkinsfile                     # Pipeline CI/CD automatisé
├── .gitignore                      # Ignore *.pkl, *.csv (sauf monitoring)
└── README.md
```

---

## 🔧 Technologies Utilisées

### **Machine Learning**
- **scikit-learn** : Preprocessing, baseline models
- **LightGBM** : Gradient Boosting (best model)
- **imbalanced-learn** : SMOTE (class balancing)
- **pandas, numpy** : Data manipulation

### **MLOps & Tracking**
- **MLflow** : Experiment tracking, model registry
- **DagsHub** : Remote MLflow server (collaboration)
- **Evidently AI** : Data drift detection, model monitoring

### **CI/CD & Deployment**
- **Jenkins** : Pipeline automation (build, test, deploy)
- **Docker** : Containerization (Backend, Frontend, Monitoring)
- **Docker Hub** : Image registry (`yessinekarray/*`)
- **GitHub Webhooks** : Auto-trigger Jenkins on push
- **ngrok** : Expose Jenkins for webhook

### **Backend & Frontend**
- **FastAPI** : RESTful API (Python, Pydantic)
- **Streamlit** : Interactive web UI
- **uvicorn** : ASGI server

---

## 🔮 Perspectives Futures (Roadmap)

### **Phase 1 : Auto-Retraining** 🤖
```
Si drift détecté → Retraining automatique
    ↓
Combine old + new data
    ↓
Train nouveau modèle
    ↓
Validation (compare performances)
    ↓
Si meilleur → Deploy | Sinon → Alerte
```

**Implémentation** :
- Jenkinsfile : Stage "Auto-Retraining si Drift"
- Scripts : `retrain_with_new_data.py`, `validate_new_model.py`
- Seuil drift : 3+ colonnes → déclenche retraining

### **Phase 2 : Model Storage Scalable** ☁️
- **MinIO** (S3-compatible, self-hosted) pour stocker modèles
- Backend télécharge modèle au démarrage (alternative au volume)
- Versioning des modèles avec tags (v1.0, v1.1, etc.)

### **Phase 3 : Kubernetes Deployment** ⚓
- Conversion docker-compose → Kubernetes manifests
- Auto-scaling backend based on load
- Rolling updates sans downtime

### **Phase 4 : A/B Testing** 🧪
- Déployer 2 versions du modèle en parallèle
- Router 50% traffic → Model A, 50% → Model B
- Comparer performances en production réelle

### **Phase 5 : Real-Time Monitoring Dashboard** 📊
- Grafana + Prometheus pour métriques temps réel
- Alertes Slack/Email si drift ou dégradation performance
- Historique des drifts et retrainings

---

## 📚 Documentation Complémentaire

### **APIs**
- **Backend Swagger** : http://localhost:8000/docs
  - `POST /predict` : Prédiction churn (JSON input)
  - `GET /health` : Health check API

### **MLflow Tracking**
- **DagsHub UI** : https://dagshub.com/YessineK/Mlops_Project
  - Experiments, runs, metrics, parameters
  - Model artifacts download

### **Evidently Reports**
- **Monitoring Dashboard** : http://localhost:9000
  - `monitoring_report.html` : Data drift visualization
  - `performance_report.html` : Model performance metrics
  - `*.json` : Tests results (PASS/FAIL)

---

## 🤝 Contribution

Ce projet a été développé dans le cadre du **Master 2 Data Science - Université Claude Bernard Lyon 1**.

**Auteur** : Yessine Karray  
**LinkedIn** : [Yessine Karray](https://www.linkedin.com/in/yessine-karray/)  
**GitHub** : [YessineK](https://github.com/YessineK)

---

## 📄 Licence

MIT License - Libre d'utilisation pour l'éducation et la recherche.

---

## 🙏 Remerciements

- **MLflow Team** pour le tracking framework
- **Evidently AI** pour les outils de monitoring
- **DagsHub** pour l'hébergement MLflow gratuit
- **FastAPI & Streamlit** pour les frameworks modernes
- **Jenkins Community** pour le CI/CD open-source

---

**⭐ Si ce projet vous a aidé, n'hésitez pas à lui donner une étoile sur GitHub !**