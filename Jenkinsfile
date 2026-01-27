pipeline {
    agent any

    environment {
        // Docker Hub
        DOCKER_HUB_USERNAME = 'yessinekarray'
        DOCKER_HUB_CREDENTIALS_ID = 'docker-hub-credentials'

        // Images
        BACKEND_IMAGE = "${DOCKER_HUB_USERNAME}/churn-backend"
        FRONTEND_IMAGE = "${DOCKER_HUB_USERNAME}/churn-frontend"

        // Tags
        IMAGE_TAG = "v${BUILD_NUMBER}"
        IMAGE_TAG_LATEST = "latest"
    }

    stages {

        stage('🧹 Cleanup Workspace') {
            steps {
                cleanWs()
                sh '''
                    echo "🧹 Nettoyage Docker safe..."
                    docker rm -f monitoring-reports || true
                    docker image prune -f --filter "dangling=true"
                '''
            }
        }

        stage('📥 Clone Repository') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/YessineK/Mlops_Project.git'
            }
        }

        stage('🔍 Verify Project Structure') {
            steps {
                sh '''
                    ls -la
                    ls -la backend/src || exit 1
                    ls -la frontend || exit 1
                    ls -la notebooks || exit 1
                '''
            }
        }

        stage('📊 Register Best Model') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/app" \
                      python:3.10-slim \
                      bash -c "
                        pip install --no-cache-dir scikit-learn pandas numpy joblib lightgbm &&
                        python /app/Jenkins/register_best_model.py
                      "
                '''
            }
        }

        stage('🔍 Validate Model Artifacts') {
            steps {
                sh '''
                    test -f backend/src/processors/models/best_model_final.pkl
                    echo "✅ Modèle validé"
                '''
            }
        }

        stage('📊 Data Drift Monitoring (Evidently)') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/app" \
                      python:3.10-slim \
                      bash -c "
                        pip install --no-cache-dir evidently pandas numpy &&
                        cd /app/monitoring &&
                        python prepare_data.py &&
                        python run_monitoring.py
                      "
                '''
            }
        }

        stage('📄 Archive Monitoring Reports') {
            steps {
                archiveArtifacts artifacts: 'monitoring/*.html', allowEmptyArchive: true
                archiveArtifacts artifacts: 'monitoring/*.json', allowEmptyArchive: true
            }
        }

        stage('🌐 Publish Monitoring Report') {
            steps {
                sh '''
                    docker build -t monitoring-reports ./monitoring
                    docker run -d \
                      --name monitoring-reports \
                      -p 9000:80 \
                      monitoring-reports
                '''
            }
        }

        stage('🐳 Build Docker Images') {
            parallel {
                stage('Backend Image') {
                    steps {
                        sh """
                            cd backend/src
                            docker build \
                              -t ${BACKEND_IMAGE}:${IMAGE_TAG} \
                              -t ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST} \
                              .
                        """
                    }
                }

                stage('Frontend Image') {
                    steps {
                        sh """
                            cd frontend
                            docker build \
                              -t ${FRONTEND_IMAGE}:${IMAGE_TAG} \
                              -t ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST} \
                              .
                        """
                    }
                }
            }
        }

        stage('🧪 Test Docker Images') {
            steps {
                sh '''
                    docker run --rm ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST} python --version
                    docker run --rm ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST} python --version
                '''
            }
        }

        stage('📤 Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: DOCKER_HUB_CREDENTIALS_ID,
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${BACKEND_IMAGE}:${IMAGE_TAG}
                        docker push ${BACKEND_IMAGE}:${IMAGE_TAG_LATEST}
                        docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}
                        docker push ${FRONTEND_IMAGE}:${IMAGE_TAG_LATEST}
                        docker logout
                    '''
                }
            }
        }

        stage('🚀 Deploy Application') {
            steps {
                sh '''
                    docker-compose down || true
                    docker-compose up -d
                    docker-compose ps
                '''
            }
        }

        stage('🏥 Health Check') {
            steps {
                sh '''
                    docker ps
                    docker-compose logs --tail=20 backend || true
                    docker-compose logs --tail=20 frontend || true
                '''
            }
        }

        stage('📊 Build Report') {
            steps {
                sh '''
                    echo "========================================"
                    echo "🎉 BUILD SUCCESS 🎉"
                    echo "Backend:  ${BACKEND_IMAGE}:${IMAGE_TAG}"
                    echo "Frontend: ${FRONTEND_IMAGE}:${IMAGE_TAG}"
                    echo "Monitoring: http://localhost:9000"
                    echo "========================================"
                '''
            }
        }
    }

    post {
        success {
            echo '✅ PIPELINE MLOps EXÉCUTÉ AVEC SUCCÈS'
        }
        failure {
            echo '❌ PIPELINE EN ÉCHEC — vérifier les logs'
        }
        always {
            sh 'docker image prune -f --filter "dangling=true" || true'
        }
    }
}
