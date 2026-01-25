# Guide de Déploiement API Heroku (Docker)

Ce guide explique comment déployer l'API `backend-mlops-fraud` sur Heroku.

## 📋 Prérequis

- Heroku CLI installé
- Docker lancé
- Application créée : `backend-mlops-fraud`

## 🚀 Étapes de Déploiement

### 1. Connexion

```bash
heroku login
heroku container:login
```

### 2. Préparation du Dockerfile (Important)

Heroku impose l'utilisation d'un port dynamique (`$PORT`). Modifiez temporairement `backend/src/Dockerfile` :

**Changer la dernière ligne :**
```dockerfile
# AVANT (Local)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# APRÈS (Pour Heroku)
CMD uvicorn api:app --host 0.0.0.0 --port $PORT
```

### 3. Build et Push

Assurez-vous d'être à la racine du projet (`MLOps/`), puis lancez :

```bash
# Définit le stack Docker (à faire une seule fois)
heroku stack:set container -a backend-mlops-fraud

# Construit et envoie l'image (utilise le Dockerfile à la racine)
heroku container:push web -a backend-mlops-fraud
```

### 4. Mise en Production

```bash
# Active l'image déployée
heroku container:release web -a backend-mlops-fraud
```

### 5. Vérification

```bash
# Voir les logs
heroku logs --tail -a backend-mlops-fraud
```

## ℹ️ Note Technique

Le `Dockerfile` à la racine du projet est configuré pour copier à la fois le code source (`backend/src`) et le registre de modèles (`notebooks/model_registry`) dans l'image Docker. Cela garantit que le modèle est disponible pour l'API en production.
