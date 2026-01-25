pipeline {
    agent any
    
    environment {
        // Docker Hub - Remplacez par vos credentials
        DOCKER_HUB_USERNAME = 'karrayyessine1'
        DOCKER_HUB_PASSWORD = '' // Laisser vide pour l'instant
        
        // Image names
        BACKEND_IMAGE = "${DOCKER_HUB_USERNAME}/churn-backend"
        FRONTEND_IMAGE = "${DOCKER_HUB_USERNAME}/churn-frontend"
        
        // Version
        IMAGE_TAG = "v${BUILD_NUMBER}"
        IMAGE_TAG_LATEST = "latest"
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
                echo '✅ Repository cloné'
            }
        }
        
        stage('🔍 Verify Structure') {
            steps {
                echo '🔍 Vérification de la structure...'
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
                '''
            }
        }
        
        stage('🐍 Setup Python') {
            steps {
                script {
                    echo '🐍 Vérification de Python...'
                    sh '''
                        if command -v python3 &> /dev/null; then
                            echo "✅ Python3 trouvé"
                            python3 --version
                        else
                            echo "⚠️ Python3 non trouvé, installation..."
                            apt-get update
                            apt-get install -y python3 python3-pip
                            python3 --version
                        fi
                    '''
                }
            }
        }
        
        stage('📊 Register Best Model') {
            steps {
                echo '📊 Exécution du script de déploiement du modèle...'
                sh '''
                    echo "🚀 Lancement de register_best_model.py"
                    python3 Jenkins/register_best_model.py
                    
                    echo ""
                    echo "✅ Script terminé"
                    
                    echo ""
                    echo "🔍 Vérification des fichiers copiés:"
                    ls -lh backend/src/processors/models/ || echo "❌ Modèle non copié!"
                '''
            }
        }
        
        stage('🔍 Validate Model') {
            steps {
                echo '🔍 Validation du modèle...'
                sh '''
                    if [ -f backend/src/processors/models/best_model_final.pkl ]; then
                        echo "✅ Modèle trouvé!"
                        ls -lh backend/src/processors/models/best_model_final.pkl
                    else
                        echo "❌ ERREUR: Modèle non trouvé!"
                        echo "Le build Docker va échouer."
                        exit 1
                    fi
                    
                    if [ -f backend/src/processors/preprocessor.pkl ]; then
                        echo "✅ Preprocessor trouvé!"
                    else
                        echo "⚠️ WARNING: Preprocessor non trouvé"
                    fi
                '''
            }
        }
        
        stage('🐳 Build Docker Images') {
            parallel {
                stage('Build Backend') {
                    steps {
                        echo '🐳 Build de l\'image Backend...'
                        sh """
                            cd backend/src
                            docker build \
                                -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                                -t ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST} \
                                --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VERSION=${IMAGE_TAG} \
                                .
                            
                            echo "✅ Backend image built: ${BACKEND_IMAGE}:${IMAGE_TAG}"
                        """
                    }
                }
                
                stage('Build Frontend') {
                    steps {
                        echo '🐳 Build de l\'image Frontend...'
                        sh """
                            cd frontend
                            docker build \
                                -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                                -t ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST} \
                                --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VERSION=${IMAGE_TAG} \
                                .
                            
                            echo "✅ Frontend image built: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                        """
                    }
                }
            }
        }
        
        stage('🧪 Test Images') {
            steps {
                echo '🧪 Test des images Docker...'
                sh '''
                    echo "🔍 Images créées:"
                    docker images | grep churn
                    
                    echo ""
                    echo "🧪 Test de l'image backend..."
                    docker run --rm ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST} python -c "print('✅ Backend OK')"
                    
                    echo ""
                    echo "🧪 Test de l'image frontend..."
                    docker run --rm ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST} python -c "print('✅ Frontend OK')"
                '''
            }
        }
        
        stage('🚀 Push to Docker Hub') {
            steps {
                script {
                    echo '⚠️ Push Docker Hub désactivé pour ce build'
                    echo '💡 Configurez Docker Hub credentials pour activer le push'
                    echo ''
                    echo '📦 Images créées localement:'
                    sh """
                        docker images | grep churn || true
                    """
                }
            }
        }
        
        stage('📊 Generate Report') {
            steps {
                echo '📊 Génération du rapport...'
                sh '''
                    echo ""
                    echo "================================================================================"
                    echo "🎉 JENKINS BUILD REPORT"
                    echo "================================================================================"
                    echo "Build Number:     ${BUILD_NUMBER}"
                    echo "Build Tag:        ${BUILD_TAG}"
                    echo "Job Name:         ${JOB_NAME}"
                    echo ""
                    echo "🐳 Docker Images:"
                    echo "   Backend:  ${BACKEND_IMAGE}:${IMAGE_TAG}"
                    echo "   Frontend: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                    echo ""
                    echo "📦 Docker Hub:"
                    echo "   https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/churn-backend"
                    echo "   https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/churn-frontend"
                    echo ""
                    echo "🚀 Déploiement:"
                    echo "   docker pull ${BACKEND_IMAGE}:latest"
                    echo "   docker pull ${FRONTEND_IMAGE}:latest"
                    echo "   docker-compose up"
                    echo ""
                    echo "✅ Build terminé avec succès!"
                    echo "================================================================================"
                    echo ""
                '''
            }
        }
    }
    
    post {
        success {
            script {
                echo '✅✅✅ PIPELINE RÉUSSI! ✅✅✅'
                echo ''
                echo '🎉 Images Docker créées:'
                echo "   Backend:  ${BACKEND_IMAGE}:${IMAGE_TAG}"
                echo "   Frontend: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
            }
        }
        
        failure {
            script {
                echo '❌❌❌ PIPELINE ÉCHOUÉ! ❌❌❌'
                echo 'Vérifiez les logs ci-dessus'
            }
        }
        
        always {
            script {
                echo '🧹 Nettoyage final...'
                echo "📊 Build ${BUILD_TAG} terminé"
            }
        }
    }
}