# 🏦 Bank Churn Prediction - MLOps Project

Système de prédiction du churn bancaire avec MLflow tracking et déploiement Docker.

## 🎯 Objectif
Prédire le risque de départ des clients bancaires avec un modèle ML (ROC-AUC: 0.993)

## 🏗️ Architecture
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **ML Tracking**: MLflow + DagsHub
- **CI/CD**: Jenkins
- **Conteneurisation**: Docker

## 📊 Modèle
- **Meilleur modèle**: LightGBM (Tuned)
- **ROC-AUC**: 0.9931
- **F1-Score**: 0.9192

## 🚀 Démarrage rapide
```bash
# Cloner le repo
git clone https://github.com/karrayyessine1/churn-mlops.git
cd churn-mlops

# Lancer avec Docker
docker-compose up --build
```

- Frontend: http://localhost:8501
- Backend API: http://localhost:8000/docs

## 📁 Structure
```
churn-mlops/
├── backend/src/          # API FastAPI
├── frontend/             # Interface Streamlit
├── notebooks/            # Notebooks ML
├── processors/           # Modèles + preprocesseurs
├── docker-compose.yml
└── Jenkinsfile
```

## 👨‍💻 Auteur
Master 2 Data Science  Claude Bernard Lyon 1