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
        
        stage('🐍 Setup Python & Register Model') {
            steps {
                echo '🐍 Configuration Python et enregistrement du modèle...'
                sh '''
                    # Installation packages
                    pip3 install --break-system-packages \
                        imbalanced-learn scikit-learn pandas numpy lightgbm joblib evidently \
                        > /dev/null 2>&1 || true
                    
                    # Registration du modèle
                    python3 Jenkins/register_best_model.py
                    
                    # Vérification
                    ls -lh backend/src/processors/models/best_model_final.pkl
                '''
            }
        }

        stage('📊 Data Drift Monitoring') {
            steps {
                echo '📊 Monitoring du data drift...'
                sh '''
                    cd monitoring
                    python3 prepare_data.py > /dev/null 2>&1
                    python3 run_monitoring.py
                    
                    # Stop ancien rapport
                    docker rm -f monitoring-reports 2>/dev/null || true
                    
                    # Publish nouveau rapport
                    docker build -t monitoring-reports . > /dev/null 2>&1
                    docker run -d --name monitoring-reports -p 9000:80 monitoring-reports
                    
                    echo "✅ Rapport accessible: http://localhost:9000"
                '''
            }
        }

        stage('📄 Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'monitoring/*.html,monitoring/*.json', 
                                allowEmptyArchive: true,
                                fingerprint: true
            }
        }

        stage('🐳 Build Docker Images') {
            parallel {
                stage('Build Backend') {
                    steps {
                        sh """
                            cd backend/src
                            docker build \
                                -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                                -t ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST} \
                                --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VERSION=${IMAGE_TAG} \
                                . > /dev/null
                            echo "✅ Backend: ${BACKEND_IMAGE}:${IMAGE_TAG}"
                        """
                    }
                }
                
                stage('Build Frontend') {
                    steps {
                        sh """
                            cd frontend
                            docker build \
                                -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                                -t ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST} \
                                --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                                --build-arg VERSION=${IMAGE_TAG} \
                                . > /dev/null
                            echo "✅ Frontend: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                        """
                    }
                }
            }
        }
        
        stage('🚀 Push to Docker Hub') {
            steps {
                script {
                    echo '📤 Push vers Docker Hub...'
                    
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-hub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin > /dev/null
                            
                            # Push en parallèle avec timeout
                            (docker push ${BACKEND_IMAGE}:${IMAGE_TAG} && \
                             docker push ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST}) &
                            PID1=$!
                            
                            (docker push ${FRONTEND_IMAGE}:${IMAGE_TAG} && \
                             docker push ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST}) &
                            PID2=$!
                            
                            # Attendre les deux push
                            wait $PID1 && echo "✅ Backend pushé"
                            wait $PID2 && echo "✅ Frontend pushé"
                            
                            docker logout > /dev/null
                        '''
                    }
                }
            }
        }
        
        stage('🚀 Deploy Application') {
            steps {
                echo '🚀 Déploiement...'
                sh '''
                    docker-compose down > /dev/null 2>&1 || true
                    docker container prune -f > /dev/null 2>&1 || true
                    docker-compose up -d
                    
                    echo ""
                    echo "✅ Services déployés:"
                    docker-compose ps
                '''
            }
        }
        
        stage('🏥 Health Check') {
            steps {
                sh '''
                    sleep 5
                    
                    # Test Backend
                    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
                        echo "✅ Backend: OK"
                    else
                        echo "⚠️  Backend: Démarrage en cours..."
                    fi
                    
                    # Test Frontend
                    if curl -f http://localhost:8501 > /dev/null 2>&1; then
                        echo "✅ Frontend: OK"
                    else
                        echo "⚠️  Frontend: Démarrage en cours..."
                    fi
                '''
            }
        }
        
        stage('📊 Build Report') {
            steps {
                sh '''
                    echo ""
                    echo "════════════════════════════════════════════════════════════════════════"
                    echo "                    🎉 BUILD #${BUILD_NUMBER} RÉUSSI"
                    echo "════════════════════════════════════════════════════════════════════════"
                    echo ""
                    echo "🐳 Images:"
                    echo "   • Backend:  ${BACKEND_IMAGE}:${IMAGE_TAG}"
                    echo "   • Frontend: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                    echo ""
                    echo "🌐 URLs:"
                    echo "   • Backend:    http://localhost:8000"
                    echo "   • Frontend:   http://localhost:8501"
                    echo "   • Monitoring: http://localhost:9000"
                    echo ""
                    echo "📦 Docker Hub:"
                    echo "   • https://hub.docker.com/r/${DOCKER_HUB_USERNAME}"
                    echo ""
                    echo "════════════════════════════════════════════════════════════════════════"
                '''
            }
        }
    }
    
    post {
        success {
            echo '✅ PIPELINE RÉUSSI - Durée: ${currentBuild.durationString}'
        }
        
        failure {
            echo '❌ PIPELINE ÉCHOUÉ - Vérifiez les logs'
        }
        
        always {
            sh 'docker image prune -f > /dev/null 2>&1 || true'
        }
    }
}