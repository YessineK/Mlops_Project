pipeline {
    agent any

    environment {
        MLFLOW_TRACKING_USERNAME = 'karrayyessine1'
        MLFLOW_TRACKING_PASSWORD = credentials('dagshub-token')
        MLFLOW_TRACKING_URI = 'https://dagshub.com/karrayyessine1/MLOps_Project.mlflow'
        DAGSHUB_TOKEN = credentials('dagshub-token')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Stop Old Containers') {
            steps {
                script {
                    echo '🛑 Stopping old containers...'
                    sh '''
                        docker rm -f churn-prediction-backend churn-prediction-frontend || true
                        docker compose down || true
                    '''
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo '🐳 Building Docker images...'
                    sh 'docker compose build'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo '🚀 Deploying...'
                    sh 'docker compose up -d'
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo '🏥 Checking health...'
                    sh '''
                        sleep 20
                        curl -f http://localhost:8000/health || exit 1
                        echo "✅ Backend is healthy"
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline succeeded!'
        }
        failure {
            echo '❌ Pipeline failed!'
            sh 'docker compose logs || true'
        }
    }
}