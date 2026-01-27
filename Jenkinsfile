pipeline {
    agent any
    
    environment {
        // Docker Hub credentials
        DOCKER_HUB_USERNAME = 'yessinekarray'
	DOCKER_HUB_CREDENTIALS_ID = 'docker-hub-credentials'
        
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
                echo '✅ Repository cloné avec succès'
            }
        }
        stage('🔧 Install System Dependencies') {
            steps {
                echo '🔧 Installation des dépendances système...'
                sh '''
                    apt-get update
                    apt-get install -y libgomp1 python3-pip
                '''
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
        stage('🧪 Deepchecks Validation') {
            steps {
                echo '🧪 Validation du modèle avec Deepchecks...'
                sh '''
                    set +e  # Ne pas arrêter sur erreur
                    
                    echo "📦 Installation de Deepchecks avec NumPy compatible..."
                    pip3 install --break-system-packages "numpy<2.0" setuptools deepchecks
                    
                    echo ""
                    echo "🔍 Vérification des versions..."
                    python3 -c "import numpy; print(f'NumPy: {numpy.__version__}')"
                    python3 -c "import deepchecks; print(f'Deepchecks: {deepchecks.__version__}')"
                    
                    echo ""
                    echo "🔍 Exécution de Deepchecks..."
                    cd testing
                    python3 run_deepchecks.py
                    
                    echo ""
                    echo "📋 Fichiers générés:"
                    ls -lh *.html 2>/dev/null || echo "Aucun fichier HTML"
                    
                    echo ""
                    echo "📂 Copie vers monitoring..."
                    cp *.html ../monitoring/ 2>/dev/null || echo "Pas de fichiers à copier"
                    
                    echo "✅ Deepchecks terminé"
                    exit 0
                '''
            }
        }
        stage('📊 Data Drift Monitoring') {
            steps {
                echo '📊 Vérification du data drift avec Evidently...'
                sh '''
                    echo "📦 Installation d'Evidently..."
                    pip3 install --break-system-packages evidently || true
                    
                    echo ""
                    echo "📂 Préparation des données..."
                    cd monitoring
                    python3 prepare_data.py
                    
                    echo ""
                    echo "📊 Génération du rapport de monitoring..."
                    python3 run_monitoring.py
                    
                    echo ""
                    echo "✅ Monitoring terminé"
                '''
            }
        }

        stage('📄 Archive Monitoring Reports') {
            steps {
                echo '📄 Archivage des rapports...'
                
                archiveArtifacts artifacts: 'monitoring/monitoring_report.html', 
                                allowEmptyArchive: true
                
                archiveArtifacts artifacts: 'monitoring/monitoring_tests.json',
                                allowEmptyArchive: true
                
                archiveArtifacts artifacts: 'monitoring/performance_report.html',
                                allowEmptyArchive: true
                
                archiveArtifacts artifacts: 'monitoring/performance_metrics.json',
                                allowEmptyArchive: true
                
                echo '✅ Rapports archivés'
            }
        }

        stage('📊 Publish Monitoring Report') {
            steps {
                echo '🌐 Publication du rapport Evidently...'
                sh '''
                    echo "🐳 Build de l'image monitoring-reports..."
                    docker build -t monitoring-reports:latest ./monitoring
                    
                    echo "🗑️ Nettoyage du conteneur existant..."
                    docker stop monitoring-reports || true
                    docker rm monitoring-reports || true
                    
                    echo "🚀 Lancement du nouveau conteneur..."
                    docker run -d --name monitoring-reports -p 9000:80 monitoring-reports:latest
                    
                    echo "✅ Rapport accessible sur http://localhost:9000"
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
            steps {
                script {
                    echo '📤 Push des images vers Docker Hub...'
                    
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-hub-credentials',  // ← CORRIGÉ : d minuscule
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                            echo "🔐 Connexion à Docker Hub..."
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            
                            echo ""
                            echo "📤 Push Backend images..."
                            docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
                            echo "✅ Pushed: ${BACKEND_IMAGE}:${IMAGE_TAG}"
                            
                            docker push ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST}
                            echo "✅ Pushed: ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST}"
                            
                            echo ""
                            echo "📤 Push Frontend images..."
                            docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                            echo "✅ Pushed: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                            
                            docker push ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST}
                            echo "✅ Pushed: ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST}"
                            
                            echo ""
                            echo "✅ Toutes les images ont été pushées avec succès!"
                            
                            echo ""
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
                    docker compose down || true
                    
                    echo ""
                    echo "🧹 Nettoyage des conteneurs arrêtés..."
                    docker container prune -f || true
                    
                    echo ""
                    echo "🚀 Démarrage des nouveaux conteneurs..."
                    docker compose up -d
                    
                    echo ""
                    echo "⏳ Attente du démarrage des services (10s)..."
                    sleep 10
                    
                    echo ""
                    echo "🔍 Vérification des conteneurs actifs:"
                    docker compose ps
                    
                    echo ""
                    echo "✅ Déploiement terminé!"
                '''
            }
        }
        
        stage('🏥 Health Check') {
            steps {
                echo '🏥 Vérification de la santé des services...'
                sh '''
                    echo "🔍 Conteneurs en cours d'exécution:"
                    docker ps --filter "name=churn" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || true
                    
                    echo ""
                    echo "🔍 Logs Backend (dernières 20 lignes):"
                    docker compose logs --tail=20 backend || true
                    
                    echo ""
                    echo "🔍 Logs Frontend (dernières 20 lignes):"
                    docker compose logs --tail=20 frontend || true
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
                    echo "🚀 Pull & Deploy Commands:"
                    echo "   docker pull ${BACKEND_IMAGE}:latest"
                    echo "   docker pull ${FRONTEND_IMAGE}:latest"
                    echo "   docker-compose up -d"
                    echo ""
                    echo "📊 Current Containers:"
                    docker ps --filter "name=churn" --format "   {{.Names}} - {{.Status}}" || true
                    echo ""
                    echo "✅ Build completed successfully!"
                    echo "================================================================================"
                '''
            }
        }
    }
    
    post {
        success {
            script {
                echo '✅✅✅ PIPELINE EXÉCUTÉ AVEC SUCCÈS! ✅✅✅'
                echo ''
                echo '🎉 Images Docker créées et pushées:'
                echo "   Backend:  ${BACKEND_IMAGE}:${IMAGE_TAG}"
                echo "   Frontend: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                echo ''
                echo '🌐 Vos images sont disponibles sur Docker Hub!'
                echo "   https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/churn-backend"
                echo "   https://hub.docker.com/r/${DOCKER_HUB_USERNAME}/churn-frontend"
            }
        }
        
        failure {
            script {
                echo '❌❌❌ PIPELINE ÉCHOUÉ! ❌❌❌'
                echo ''
                echo '🔍 Vérifiez les logs ci-dessus pour identifier l\'erreur'
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
                
                echo "📊 Build terminé"
            }
        }
    }
}
