#!/bin/bash

# Script pour exécuter Deepchecks dans un conteneur Docker séparé avec Python 3.11

set -e

echo "════════════════════════════════════════════════════════"
echo "  🐳 DEEPCHECKS VALIDATION - DOCKER ISOLÉ"
echo "════════════════════════════════════════════════════════"

# Créer un Dockerfile temporaire pour Deepchecks
cat > /tmp/Dockerfile.deepchecks << 'DOCKERFILE'
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     g++     && rm -rf /var/lib/apt/lists/*

# Installer l'écosystème Deepchecks compatible
RUN pip install --no-cache-dir     pandas==1.5.3     scikit-learn==1.3.2     deepchecks==0.17.3     numpy==1.24.3     matplotlib     plotly     ipython==7.34.0     ipywidgets==7.8.1

# Script d'exécution
COPY run_deepchecks.py /app/
COPY best_model_final.pkl /app/ 2>/dev/null || true

CMD ["python", "run_deepchecks.py"]
DOCKERFILE

echo ""
echo "📦 Construction de l'image Docker Deepchecks..."
docker build -f /tmp/Dockerfile.deepchecks -t deepchecks-validator:latest . 2>&1 | tail -n 20

echo ""
echo "🔍 Copie des fichiers nécessaires..."
mkdir -p /tmp/deepchecks_build
cp testing/run_deepchecks.py /tmp/deepchecks_build/ 2>/dev/null || echo "⚠️ Script non trouvé"

if [ -f "backend/src/processors/models/best_model_final.pkl" ]; then
    cp backend/src/processors/models/best_model_final.pkl /tmp/deepchecks_build/
elif [ -f "processors/models/best_model_final.pkl" ]; then
    cp processors/models/best_model_final.pkl /tmp/deepchecks_build/
else
    echo "⚠️ Modèle non trouvé"
fi

echo ""
echo "🚀 Exécution de Deepchecks dans le conteneur..."
docker run --rm     -v /tmp/deepchecks_build/run_deepchecks.py:/app/run_deepchecks.py     -v /tmp/deepchecks_build/best_model_final.pkl:/app/best_model_final.pkl     -v "$(pwd)/testing":/app/output     deepchecks-validator:latest

echo ""
echo "📋 Vérification des rapports générés..."
ls -lh testing/*.html 2>/dev/null || echo "❌ Aucun rapport HTML généré"

echo ""
echo "🧹 Nettoyage..."
docker rmi deepchecks-validator:latest 2>/dev/null || true

echo ""
echo "✅ Deepchecks terminé !"
echo "════════════════════════════════════════════════════════"
