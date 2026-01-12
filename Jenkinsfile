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
                    sh '''
                        docker compose down
                        docker compose up -d
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo '🏥 Checking health...'
                    sh '''
                        sleep 15
                        curl -f http://localhost:8000/health || exit 1
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
        }
    }
}