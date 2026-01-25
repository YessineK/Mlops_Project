# CI/CD Pipeline pour MLOps - Jenkins

Ce dossier contient la configuration nécessaire pour déployer un pipeline Jenkins dédié à l'entraînement continu (Continuous Training) des modèles de détection de fraude.

## 📁 Contenu

*   **train_model.py** : Script d'entraînement (4 modèles baseline).
*   **register_best_model.py** : Sélection et enregistrement du meilleur modèle.
*   **Dockerfile** : Image Jenkins personnalisée incluant Python 3 et les outils de build nécessaires.
*   **Jenkinsfile.txt** : Définition du pipeline (Setup, Training, Register, Test, Deploy).

## 🚀 Mise en place

### 1. Construire et Lancer Jenkins

Dans ce répertoire (`Jenkins`), lancez :

```bash
# Construire l'image
docker build -t jenkins-mlops .

# Lancer le conteneur
# Note : on monte le socket docker si besoin de docker-in-docker, 
# et un volume pour la persistance
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins-mlops \
  jenkins-mlops
```

### 2. Configuration Initiale

1.  Accédez à `http://localhost:8080`.
2.  Récupérez le mot de passe administrateur : `docker exec jenkins-mlops cat /var/jenkins_home/secrets/initialAdminPassword`.
3.  Installez les plugins recommandés.

### 3. Configuration du Pipeline

1.  **Créer un nouveau Job** : Sélectionnez "Pipeline".
2.  **Definition** : Choisissez "Pipeline script from SCM".
3.  **SCM** : Git.
4.  **Repository URL** : Votre URL DagsHub ou locale.
5.  **Script Path** : `Jenkins/Jenkinsfile.txt`.

### 4. Credentials

Pour que MLflow puisse communiquer avec DagsHub, ajoutez un credential dans Jenkins :

*   **Type** : Secret Text
*   **ID** : `dagshub-token`
*   **Secret** : Votre token DagsHub (voir `.env` ou settings DagsHub).

## 📊 Pipeline Steps

1.  **Checkout** : Récupération du code.
2.  **Setup Environment** : Création venv, installation `requirements.txt`.
3.  **Continuous Training** : Exécution de `Jenkins/train_model.py`.
    *   Entraîne 4 modèles (RandomForest, XGBoost, LightGBM, CatBoost).
    *   Le script gère le tracking MLflow.
4.  **Register Best Model** : Exécution de `Jenkins/register_best_model.py`.
    *   Sélectionne le meilleur run (ROC-AUC).
    *   Enregistre et télécharge le modèle pour le test.
5.  **Run Tests** : Validation avec `test_fraud_scenario.py`.
6.  **Build and Deploy** : Redéploiement via Docker Compose.

## 🔄 Déclenchement

Le pipeline peut être configuré pour se lancer :
*   Périodiquement (Cron).
*   Via Webhook (Push sur GitHub/DagsHub).
