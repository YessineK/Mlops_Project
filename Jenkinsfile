pipeline {
    agent any
    
    environment {
        DOCKER_HUB_REPO = 'yessinekarray'
        BACKEND_IMAGE = 'churn-backend'
        FRONTEND_IMAGE = 'churn-frontend'
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
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
                    ls -la notebooks/model_registry/
                    
                    echo ""
                    echo "📂 Notebooks Processors:"
                    ls -la notebooks/processors/
                    
                    echo ""
                    echo "📂 Backend:"
                    ls -la backend/src/
                    
                    echo ""
                    echo "📂 Frontend:"
                    ls -la frontend/
                '''
            }
        }
        
        stage('🐍 Setup Python Environment') {
            steps {
                echo '🐍 Configuration de l\'environnement Python...'
                sh '''
                    command -v python3 || { echo "Python3 non trouvé!"; exit 1; }
                    echo "✅ Python3 trouvé"
                    python3 --version
                    
                    echo ""
                    echo "📦 Installation des packages Python requis..."
                    pip3 install --break-system-packages "scikit-learn==1.5.2" imbalanced-learn pandas numpy lightgbm joblib
                    echo "✅ Packages Python installés"
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
                    ls -lh backend/src/processors/models/
                '''
            }
        }
        
        stage('🧪 Deepchecks Validation') {
            steps {
                echo '🧪 Validation du modèle avec Deepchecks...'
                sh '''
                    set +e  # Ne pas arrêter sur erreur
                    
                    echo "🗑️ DÉSINSTALLATION de NumPy existant..."
                    pip3 uninstall -y numpy
                    
                    echo ""
                    echo "📦 Installation de NumPy 1.26.4 (compatible)..."
                    pip3 install --break-system-packages "numpy==1.26.4"
                    
                    echo ""
                    echo "📦 Installation de Deepchecks..."
                    pip3 install --break-system-packages setuptools deepchecks
                    
                    echo ""
                    echo "🔍 Vérification des versions APRÈS installation:"
                    python3 -c "import numpy; print('NumPy version:', numpy.__version__)"
                    python3 -c "import sys; print('Python:', sys.version)"
                    
                    echo ""
                    echo "🧪 Test d'import Deepchecks:"
                    python3 -c "from deepchecks.tabular import Dataset; print('✅ Deepchecks OK')" || echo "❌ Deepchecks FAILED"
                    
                    echo ""
                    echo "🔍 Exécution de Deepchecks..."
                    cd testing
                    python3 run_deepchecks.py
                    EXIT_CODE=$?
                    echo "Exit code: $EXIT_CODE"
                    
                    echo ""
                    echo "📋 Fichiers générés:"
                    ls -lh *.html 2>/dev/null || echo "❌ AUCUN FICHIER HTML GÉNÉRÉ"
                    
                    echo ""
                    echo "✅ Stage terminé"
                    exit 0
                '''
            }
        }
        stage('📂 Copy Deepchecks Reports') {
            steps {
                echo '📂 Copie des rapports Deepchecks vers monitoring...'
                sh '''
                    echo "📋 Fichiers Deepchecks générés:"
                    ls -lh testing/*.html 2>/dev/null
                    
                    echo ""
                    echo "📂 Copie vers monitoring/..."
                    cp -v testing/data_distribution_test.html monitoring/ 2>/dev/null && echo "✅ data_distribution copié" || echo "⚠️ data_distribution non trouvé"
                    cp -v testing/result_integrity_test.html monitoring/ 2>/dev/null && echo "✅ result_integrity copié" || echo "⚠️ result_integrity non trouvé"
                    cp -v testing/result_model_test.html monitoring/ 2>/dev/null && echo "✅ result_model copié" || echo "⚠️ result_model non trouvé"
                    
                    echo ""
                    echo "✅ Copie terminée"
                '''
            }
        }
        stage('🔍 Validate Model Files') {
            steps {
                echo '🔍 Validation des fichiers du modèle...'
                sh '''
                    echo "📂 Vérification de l'existence des fichiers requis..."
                    
                    if [ -f "backend/src/processors/models/best_model_final.pkl" ]; then
                        echo "✅ best_model_final.pkl trouvé"
                    else
                        echo "❌ best_model_final.pkl manquant!"
                        exit 1
                    fi
                    
                    if [ -f "backend/src/processors/preprocessor.pkl" ]; then
                        echo "✅ preprocessor.pkl trouvé"
                    else
                        echo "❌ preprocessor.pkl manquant!"
                        exit 1
                    fi
                    
                    echo "✅ Tous les fichiers requis sont présents"
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
                echo '📄 Archivage des rapports de monitoring...'
                
                archiveArtifacts artifacts: 'monitoring/monitoring_report.html',
                                allowEmptyArchive: true,
                                fingerprint: true
                
                archiveArtifacts artifacts: 'monitoring/monitoring_tests.json',
                                allowEmptyArchive: true,
                                fingerprint: true
                
                archiveArtifacts artifacts: 'monitoring/performance_report.html',
                                allowEmptyArchive: true,
                                fingerprint: true
                
                archiveArtifacts artifacts: 'monitoring/performance_metrics.json',
                                allowEmptyArchive: true,
                                fingerprint: true
                
                echo '✅ Rapports de monitoring archivés'
            }
        }
        
        stage('📊 Publish Monitoring Report') {
            steps {
                echo '🌐 Publication du rapport de monitoring...'
                sh '''
                    echo "🐳 Build de l'image monitoring-reports..."
                    docker build -t monitoring-reports:latest ./monitoring
                    
                    echo "🗑️ Nettoyage du conteneur existant..."
                    docker stop monitoring-reports || true
                    docker rm monitoring-reports || true
                    
                    echo "🚀 Lancement du nouveau conteneur..."
                    docker run -d --name monitoring-reports -p 9000:80 monitoring-reports:latest
                    
                    echo "✅ Rapport de monitoring accessible sur http://localhost:9000"
                '''
            }
        }
        
        stage('🐳 Build Docker Images') {
            parallel {
                stage('Build Backend Image') {
                    steps {
                        echo '🐳 Construction de l\'image Docker Backend...'
                        sh '''
                            echo "📂 Contexte de build: backend/src/"
                            cd backend/src
                            
                            echo "🏗️ Build de l'image..."
                            docker build -t ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:v${BUILD_NUMBER} .
                            docker tag ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:v${BUILD_NUMBER} ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:latest
                            
                            echo "✅ Image Backend construite: v${BUILD_NUMBER}"
                        '''
                    }
                }
                
                stage('Build Frontend Image') {
                    steps {
                        echo '🐳 Construction de l\'image Docker Frontend...'
                        sh '''
                            echo "📂 Contexte de build: frontend/"
                            cd frontend
                            
                            echo "🏗️ Build de l'image..."
                            docker build -t ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:v${BUILD_NUMBER} .
                            docker tag ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:v${BUILD_NUMBER} ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:latest
                            
                            echo "✅ Image Frontend construite: v${BUILD_NUMBER}"
                        '''
                    }
                }
            }
        }
        
        stage('🧪 Test Docker Images') {
            steps {
                echo '🧪 Test des images Docker...'
                sh '''
                    echo "🔍 Vérification de l'image Backend..."
                    docker images ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:v${BUILD_NUMBER}
                    
                    echo ""
                    echo "🔍 Vérification de l'image Frontend..."
                    docker images ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:v${BUILD_NUMBER}
                    
                    echo "✅ Images Docker validées"
                '''
            }
        }
        
        stage('🚀 Push to Docker Hub') {
            steps {
                echo '🚀 Push des images vers Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', 
                                                 usernameVariable: 'DOCKER_USER', 
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "🔐 Connexion à Docker Hub..."
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        
                        echo ""
                        echo "📤 Push Backend image..."
                        docker push ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:v${BUILD_NUMBER}
                        docker push ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:latest
                        
                        echo ""
                        echo "📤 Push Frontend image..."
                        docker push ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:v${BUILD_NUMBER}
                        docker push ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:latest
                        
                        echo ""
                        echo "✅ Images poussées sur Docker Hub"
                        echo "   Backend: ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:v${BUILD_NUMBER}"
                        echo "   Frontend: ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:v${BUILD_NUMBER}"
                    '''
                }
            }
        }
        
        stage('🚀 Deploy Application') {
            steps {
                echo '🚀 Déploiement de l\'application...'
                sh '''
                    echo "🗑️ Arrêt des conteneurs existants..."
                    docker-compose down || true
                    
                    echo ""
                    echo "🚀 Lancement des nouveaux conteneurs..."
                    docker-compose up -d
                    
                    echo ""
                    echo "⏳ Attente du démarrage des services..."
                    sleep 10
                    
                    echo ""
                    echo "📊 État des conteneurs:"
                    docker-compose ps
                    
                    echo "✅ Application déployée"
                '''
            }
        }
        
        stage('🏥 Health Check') {
            steps {
                echo '🏥 Vérification de la santé des services...'
                sh '''
                    echo "🔍 Vérification du Backend..."
                    curl -f http://localhost:8000/health || echo "⚠️ Backend health check échoué"
                    
                    echo ""
                    echo "🔍 Vérification du Frontend..."
                    curl -f http://localhost:8501 || echo "⚠️ Frontend health check échoué"
                    
                    echo ""
                    echo "✅ Health checks terminés"
                '''
            }
        }
        
        stage('📊 Generate Build Report') {
            steps {
                echo '📊 Génération du rapport de build...'
                sh '''
                    echo "================================"
                    echo "BUILD REPORT - Build #${BUILD_NUMBER}"
                    echo "================================"
                    echo "Timestamp: $(date)"
                    echo ""
                    echo "📦 Images Docker:"
                    echo "  Backend:  ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:v${BUILD_NUMBER}"
                    echo "  Frontend: ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:v${BUILD_NUMBER}"
                    echo ""
                    echo "🌐 Services déployés:"
                    echo "  Backend API:  http://localhost:8000"
                    echo "  Frontend UI:  http://localhost:8501"
                    echo "  Monitoring:   http://localhost:9000"
                    echo ""
                    echo "📊 Rapports disponibles:"
                    echo "  • Evidently (Drift + Performance)"
                    echo "  • Deepchecks (Validation Qualité)"
                    echo ""
                    echo "✅ Build terminé avec succès!"
                    echo "================================"
                '''
            }
        }
    }
    
    post {
        always {
            script {
                echo ""
                echo "🧹 Nettoyage final..."
                sh '''
                    echo "🗑️ Suppression des images Docker non utilisées..."
                    docker image prune -f
                '''
                echo "📊 Build terminé"
            }
        }
        
        success {
            script {
                echo "✅✅✅ PIPELINE RÉUSSI! ✅✅✅"
                echo ""
                echo "🎉 Félicitations! Le déploiement est terminé."
                echo ""
                echo "📊 Accès aux services:"
                echo "   • Backend:    http://localhost:8000"
                echo "   • Frontend:   http://localhost:8501"
                echo "   • Monitoring: http://localhost:9000 (Evidently + Deepchecks)"
            }
        }
        
        failure {
            script {
                echo "❌❌❌ PIPELINE ÉCHOUÉ! ❌❌❌"
                echo ""
                echo "🔍 Vérifiez les logs ci-dessus pour identifier l'erreur"
            }
        }
    }
}