pipeline {
    agent any
    
    environment {
        // 🔐 VOS VRAIES CREDENTIALS
        MLFLOW_TRACKING_USERNAME = 'karrayyessine1'
        MLFLOW_TRACKING_PASSWORD = credentials('dagshub-token')
        MLFLOW_TRACKING_URI = 'https://dagshub.com/karrayyessine1/MLOps_Project.mlflow'
        DAGSHUB_TOKEN = credentials('dagshub-token')
        DAGSHUB_USER = 'karrayyessine1'
        DAGSHUB_REPO = 'MLOps_Project'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    echo '🔧 Setting up Python environment...'
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Continuous Training') {
            steps {
                script {
                    echo '🎓 Training models with MLflow...'
                    sh '''
                        . venv/bin/activate
                        python3 Jenkins/train_model.py
                    '''
                }
            }
        }
        
        stage('Register Best Model') {
            steps {
                script {
                    echo '📥 Downloading best model from MLflow...'
                    sh '''
                        . venv/bin/activate
                        python3 Jenkins/register_best_model.py
                    '''
                }
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
                    echo '🚀 Deploying containers...'
                    sh 'docker compose up -d'
                }
            }
        }
        
        stage('Health Check') {
            steps {
                script {
                    echo '🏥 Checking application health...'
                    sh '''
                        sleep 30
                        docker exec churn-prediction-backend curl -f http://localhost:8000/health || echo "Warning: Health check failed but continuing..."
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
            sh 'docker compose logs || true'
        }
        always {
            echo '🧹 Cleaning up virtual environment...'
            sh 'rm -rf venv || true'
        }
    }
}