pipeline {
    agent {
        docker {
            image 'python:3.10'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        DOCKER_HUB_REPO = 'yessinekarray'
        BACKEND_IMAGE  = 'churn-backend'
        FRONTEND_IMAGE = 'churn-frontend'
        BUILD_NUMBER   = "${env.BUILD_NUMBER}"
    }

    stages {

        stage('📥 Clone Repository') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/YessineK/Mlops_Project.git'
            }
        }

        stage('🐍 Setup Python Environment') {
            steps {
                sh '''
                python3 --version

                export PIP_TARGET=$WORKSPACE/.pip
                export PYTHONPATH=$PIP_TARGET
                export PATH=$PIP_TARGET/bin:$PATH

                pip install scikit-learn==1.5.2 \
                            imbalanced-learn \
                            pandas numpy lightgbm joblib \
                            evidently
                '''
            }
        }

        stage('📊 Register Best Model') {
            steps {
                sh '''
                python3 Jenkins/register_best_model.py
                ls -lh backend/src/processors/models/
                '''
            }
        }

        stage('🧪 Deepchecks Validation (Docker)') {
            steps {
                sh '''
                echo "🐳 Deepchecks Docker Validation"

                docker --version
                docker ps > /dev/null

                sh run_deepchecks_docker.sh || true

                ls -lh testing/*.html || true
                '''
            }
        }

        stage('📂 Copy Deepchecks Report') {
            steps {
                sh '''
                mkdir -p monitoring
                cp testing/deepchecks_summary.html monitoring/ || true
                ls -lh monitoring/
                '''
            }
        }

        stage('📊 Data Drift Monitoring') {
            steps {
                sh '''
                cd monitoring
                python3 prepare_data.py
                python3 run_monitoring.py
                '''
            }
        }

        stage('📄 Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'monitoring/*.html',
                                 allowEmptyArchive: true,
                                 fingerprint: true
            }
        }

        stage('🐳 Build Docker Images') {
            parallel {
                stage('Backend Image') {
                    steps {
                        sh '''
                        cd backend/src
                        docker build -t ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:v${BUILD_NUMBER} .
                        docker tag ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:v${BUILD_NUMBER} \
                                   ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:latest
                        '''
                    }
                }

                stage('Frontend Image') {
                    steps {
                        sh '''
                        cd frontend
                        docker build -t ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:v${BUILD_NUMBER} .
                        docker tag ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:v${BUILD_NUMBER} \
                                   ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:latest
                        '''
                    }
                }
            }
        }

        stage('🚀 Push Docker Images') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin

                    docker push ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:v${BUILD_NUMBER}
                    docker push ${DOCKER_HUB_REPO}/${BACKEND_IMAGE}:latest
                    docker push ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:v${BUILD_NUMBER}
                    docker push ${DOCKER_HUB_REPO}/${FRONTEND_IMAGE}:latest
                    '''
                }
            }
        }

        stage('🚀 Deploy Application') {
            steps {
                sh '''
                docker compose down || true
                docker compose up -d
                docker compose ps
                '''
            }
        }

        stage('🏥 Health Check') {
            steps {
                sh '''
                curl -f http://localhost:8000/health || true
                curl -f http://localhost:8501 || true
                '''
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
        }

        success {
            echo '✅ PIPELINE RÉUSSI'
            echo 'Backend    : http://localhost:8000'
            echo 'Frontend   : http://localhost:8501'
            echo 'Monitoring : http://localhost:9000'
        }

        failure {
            echo '❌ PIPELINE ÉCHOUÉ — voir logs'
        }
    }
}
