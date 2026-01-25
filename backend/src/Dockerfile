FROM python:3.12-slim

# Metadata
LABEL maintainer="karrayyessine1@gmail.com"
LABEL description="Churn Prediction Backend API"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./

# Copy processors directory (contient le modèle copié par Jenkins)
COPY processors/ ./processors/

# Vérifier que le modèle existe (CRITIQUE)
RUN if [ ! -f /app/processors/models/best_model_final.pkl ]; then \
        echo ""; \
        echo "❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌"; \
        echo "❌ ERREUR CRITIQUE: MODÈLE NON TROUVÉ!"; \
        echo "❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌"; \
        echo ""; \
        echo "Le fichier best_model_final.pkl n'existe pas!"; \
        echo ""; \
        echo "🔧 SOLUTION:"; \
        echo "   Jenkins doit exécuter ce script AVANT le build:"; \
        echo "   → python Jenkins/register_best_model.py"; \
        echo ""; \
        echo "📂 Contenu actuel de /app/processors/:"; \
        ls -lah /app/processors/ 2>/dev/null || echo "   (vide)"; \
        echo ""; \
        echo "❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌"; \
        exit 1; \
    fi && \
    echo "✅ Modèle trouvé: /app/processors/models/best_model_final.pkl" && \
    ls -lh /app/processors/models/best_model_final.pkl

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Run API (le modèle est déjà dans l'image)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]