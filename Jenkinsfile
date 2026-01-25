pipeline {
    agent any
    
    environment {
        // Docker Hub credentials
        DOCKER_HUB_USERNAME = 'karrayyessine1'
        DOCKER_HUB_CREDENTIALS = 'docker-hub-credentials' // ID dans Jenkins Credentials
        
        // Image names
        BACKEND_IMAGE = "${DOCKER_HUB_USERNAME}/churn-backend"
        FRONTEND_IMAGE = "${DOCKER_HUB_USERNAME}/churn-frontend"
        
        // Version
        IMAGE_TAG = "v${BUILD_NUMBER}"
        IMAGE_TAG_LATEST = "latest"
        
        // Workspace path
        WORKSPACE_PATH = "/var/jenkins_home/workspace/${JOB_NAME}"
    }
    
    stages {
        
        stage('🧹 Cleanup') {
            steps {
                echo '🧹 Nettoyage du workspace...'
                cleanWs()
            }
        }
        
        stage('📥 Clone Repository') {
            steps {
                echo '📥 Clone du repository GitHub...'
                git branch: 'main',
                    url: 'https://github.com/YessineK/Mlops_Project.git'
                echo '✅ Repository cloné avec succès'
            }
        }
        
        stage('🔍 Verify Structure') {
            steps {
                echo '🔍 Vérification de la structure du projet...'
                sh '''
                    echo "📂 Structure du projet:"
                    ls -la
                    
                    echo ""
                    echo "📂 Model Registry:"
                    ls -la notebooks/model_registry/ || echo "❌ Model registry non trouvé"
                    
                    echo ""
                    echo "📂 Notebooks Processors:"
                    ls -la notebooks/processors/ || echo "❌ Processors non trouvés"
                    
                    echo ""
                    echo "📂 Backend:"
                    ls -la backend/src/ || echo "❌ Backend non trouvé"
                    
                    echo ""
                    echo "📂 Frontend:"
                    ls -la frontend/ || echo "❌ Frontend non trouvé"
                '''
            }
        }
        
        stage('🐍 Setup Python Environment') {
            steps {
                echo '🐍 Configuration de l\'environnement Python...'
                sh '''
                    if command -v python3 &> /dev/null; then
                        echo "✅ Python3 trouvé"
                        python3 --version
                        
                        echo ""
                        echo "📦 Installation des packages Python requis..."
                        pip3 install --break-system-packages \
                            imbalanced-learn \
                            scikit-learn \
                            pandas \
                            numpy \
                            lightgbm \
                            joblib || true
                        
                        echo "✅ Packages Python installés"
                    else
                        echo "❌ Python3 non trouvé!"
                        exit 1
                    fi
                '''
            }
        }
        
        stage('📊 Register Best Model') {
            steps {
                echo '📊 Enregistrement du meilleur modèle...'
                sh '''
                    echo "🚀 Exécution de register_best_model.py"
                    python3 Jenkins/register_best_model.py
                    
                    echo ""
                    echo "✅ Script de registration terminé"
                    
                    echo ""
                    echo "🔍 Vérification des fichiers générés:"
                    ls -lh backend/src/processors/models/ || echo "❌ Dossier models non trouvé!"
                '''
            }
        }
        
        stage('🔍 Validate Model Files') {
            steps {
                echo '🔍 Validation des fichiers du modèle...'
                sh '''
                    MODEL_FILE="backend/src/processors/models/best_model_final.pkl"
                    PREPROCESSOR_FILE="backend/src/processors/preprocessor.pkl"
                    
                    echo "🔎 Vérification du modèle..."
                    if [ -f "$MODEL_FILE" ]; then
                        echo "✅ Modèle trouvé: $MODEL_FILE"
                        ls -lh "$MODEL_FILE"
                    else
                        echo "❌ ERREUR CRITIQUE: Modèle non trouvé!"
                        echo "Le fichier $MODEL_FILE est requis pour le build Docker."
                        exit 1
                    fi
                    
                    echo ""
                    echo "🔎 Vérification du preprocessor..."
                    if [ -f "$PREPROCESSOR_FILE" ]; then
                        echo "✅ Preprocessor trouvé: $PREPROCESSOR_FILE"
                        ls -lh "$PREPROCESSOR_FILE"
                    else
                        echo "⚠️  WARNING: Preprocessor non trouvé à $PREPROCESSOR_FILE"
                        echo "Cela pourrait causer des problèmes lors de l'exécution."
                    fi
                '''
            }
        }
        
        stage('🐳 Build Docker Images') {
            parallel {
                stage('Build Backend Image') {
                    steps {
                        echo '🐳 Construction de l\'image Backend...'
                        sh """
                            cd backend/src
                            
                            echo "🔨 Build de l'image Backend..."
                            docker build \
                                -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                                -t ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST} \
                                --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VERSION=${IMAGE_TAG} \
                                --build-arg BUILD_NUMBER=${BUILD_NUMBER} \
                                .
                            
                            echo "✅ Backend image construite: ${BACKEND_IMAGE}:${IMAGE_TAG}"
                        """
                    }
                }
                
                stage('Build Frontend Image') {
                    steps {
                        echo '🐳 Construction de l\'image Frontend...'
                        sh """
                            cd frontend
                            
                            echo "🔨 Build de l'image Frontend..."
                            docker build \
                                -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                                -t ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST} \
                                --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VERSION=${IMAGE_TAG} \
                                --build-arg BUILD_NUMBER=${BUILD_NUMBER} \
                                .
                            
                            echo "✅ Frontend image construite: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                        """
                    }
                }
            }
        }
        
        stage('🧪 Test Docker Images') {
            steps {
                echo '🧪 Test des images Docker construites...'
                sh '''
                    echo "🔍 Images Docker disponibles:"
                    docker images | grep churn || echo "❌ Aucune image trouvée!"
                    
                    echo ""
                    echo "🧪 Test de l'image Backend..."
                    docker run --rm ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST} python --version
                    echo "✅ Backend image fonctionne"
                    
                    echo ""
                    echo "🧪 Test de l'image Frontend..."
                    docker run --rm ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST} python --version
                    echo "✅ Frontend image fonctionne"
                '''
            }
        }
        
        stage('🚀 Push to Docker Hub') {
            when {
                expression { 
                    // Active le push seulement si les credentials existent
                    return env.DOCKER_HUB_CREDENTIALS != null 
                }
            }
            steps {
                script {
                    echo '📤 Push des images vers Docker Hub...'
                    withCredentials([usernamePassword(
                        credentialsId: "${DOCKER_HUB_CREDENTIALS}",
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                            echo "🔐 Connexion à Docker Hub..."
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            
                            echo ""
                            echo "📤 Push Backend images..."
                            docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
                            docker push ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST}
                            
                            echo ""
                            echo "📤 Push Frontend images..."
                            docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                            docker push ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST}
                            
                            echo ""
                            echo "✅ Toutes les images ont été pushées avec succès!"
                            
                            echo "🔓 Déconnexion de Docker Hub..."
                            docker logout
                        '''
                    }
                }
            }
        }
        
        stage('🚀 Deploy Application') {
            steps {
                echo '🚀 Déploiement de l\'application...'
                sh '''
                    echo "📂 Navigation vers le workspace..."
                    cd "${WORKSPACE}"
                    
                    echo ""
                    echo "🛑 Arrêt des conteneurs existants..."
                    docker-compose down || true
                    
                    echo ""
                    echo "🧹 Nettoyage des conteneurs arrêtés..."
                    docker container prune -f || true
                    
                    echo ""
                    echo "🚀 Démarrage des nouveaux conteneurs..."
                    docker-compose up -d
                    
                    echo ""
                    echo "⏳ Attente du démarrage des services (10s)..."
                    sleep 10
                    
                    echo ""
                    echo "🔍 Vérification des conteneurs actifs:"
                    docker-compose ps
                    
                    echo ""
                    echo "🔍 Conteneurs en cours d'exécution:"
                    docker ps --filter "name=churn" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
                    
                    echo ""
                    echo "✅ Déploiement terminé!"
                '''
            }
        }
        
        stage('🏥 Health Check') {
            steps {
                echo '🏥 Vérification de la santé des services...'
                sh '''
                    echo "🔍 Test de connectivité Backend..."
                    sleep 5
                    
                    # Tentative de connexion au backend (ajustez le port si nécessaire)
                    curl -f http://localhost:8000/health || echo "⚠️  Backend health check échoué"
                    
                    echo ""
                    echo "🔍 Logs Backend (dernières lignes):"
                    docker-compose logs --tail=20 backend || true
                    
                    echo ""
                    echo "🔍 Logs Frontend (dernières lignes):"
                    docker-compose logs --tail=20 frontend || true
                '''
            }
        }
        
        stage('📊 Generate Build Report') {
            steps {
                echo '📊 Génération du rapport de build...'
                sh '''
                    echo ""
                    echo "================================================================================"
                    echo "                       🎉 JENKINS BUILD REPORT 🎉"
                    echo "================================================================================"
                    echo ""
                    echo "📋 Build Information:"
                    echo "   Build Number:     #${BUILD_NUMBER}"
                    echo "   Build Tag:        ${BUILD_TAG}"
                    echo "   Job Name:         ${JOB_NAME}"
                    echo "   Build URL:        ${BUILD_URL}"
                    echo "   Timestamp:        $(date)"
                    echo ""
                    echo "🐳 Docker Images Created:"
                    echo "   Backend:          ${BACKEND_IMAGE}:${IMAGE_TAG}"
                    echo "   Backend (latest): ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST}"
                    echo "   Frontend:         ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                    echo "   Frontend (latest):${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST}"
                    echo ""
                    echo "📦 Docker Hub Links:"
                    echo "   Backend:  https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/churn-backend"
                    echo "   Frontend: https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/churn-frontend"
                    echo ""
                    echo "🚀 Deployment Commands:"
                    echo "   Pull images:"
                    echo "     docker pull ${BACKEND_IMAGE}:latest"
                    echo "     docker pull ${FRONTEND_IMAGE}:latest"
                    echo ""
                    echo "   Deploy with docker-compose:"
                    echo "     docker-compose up -d"
                    echo ""
                    echo "📊 Current Containers:"
                    docker ps --filter "name=churn" --format "   {{.Names}} - {{.Status}}"
                    echo ""
                    echo "✅ Build completed successfully!"
                    echo "================================================================================"
                    echo ""
                '''
            }
        }
    }
    
    post {
        success {
            script {
                echo '✅✅✅ PIPELINE EXÉCUTÉ AVEC SUCCÈS! ✅✅✅'
                echo ''
                echo '🎉 Images Docker créées et déployées:'
                echo "   Backend:  ${BACKEND_IMAGE}:${IMAGE_TAG}"
                echo "   Frontend: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                echo ''
                echo '🌐 Application disponible localement'
            }
        }
        
        failure {
            script {
                echo '❌❌❌ PIPELINE ÉCHOUÉ! ❌❌❌'
                echo ''
                echo '🔍 Vérifiez les logs ci-dessus pour identifier l\'erreur'
                echo ''
                echo '💡 Erreurs communes:'
                echo '   - Modèle ML non trouvé'
                echo '   - Dockerfile manquant ou incorrect'
                echo '   - docker-compose.yml manquant'
                echo '   - Port déjà utilisé'
            }
        }
        
        always {
            script {
                echo ''
                echo '🧹 Nettoyage final...'
                
                sh '''
                    echo "🗑️  Suppression des images Docker non utilisées..."
                    docker image prune -f || true
                '''
                
                echo "📊 Build ${BUILD_TAG} terminé"
            }
        }
    }
}
