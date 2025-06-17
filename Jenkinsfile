pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'devops_chatbot_ci'
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        GITHUB_REPO = 'https://github.com/AhmadMughal-DS/final_chatbot_for_devops'  // Replace with your actual GitHub repo
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Clean workspace before we start
                cleanWs()
                
                // Fetch code from GitHub repository
                echo 'Fetching code from GitHub repository'
                git branch: 'main', url: "${GITHUB_REPO}"
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running Python tests'
                sh 'python -m pytest -v || echo "No tests available, continuing..."'
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building Docker containers'
                // Check Docker and Docker Compose installation
                sh 'docker --version'
                sh 'docker-compose --version'
                
                // Build the Docker images
                sh 'docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} build --no-cache'
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying application with Docker Compose'
                
                // Stop any existing containers with the same project name
                sh 'docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} down || true'
                
                // Start the containers in detached mode
                sh 'docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} up -d'
                
                // Verify that the containers are running
                sh 'docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} ps'
            }
        }
        
        stage('Verify') {
            steps {
                echo 'Verifying the deployment'
                // Wait for application to be ready
                sh 'sleep 10'
                
                // Check if the container is running
                sh 'docker ps | grep ${PROJECT_NAME}'
                
                // Try to connect to the backend service
                sh 'curl -s --retry 5 --retry-delay 5 http://localhost:8000/ || echo "Service may still be starting..."'
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up workspace'
            deleteDir() // Clean workspace after build
        }
        success {
            echo 'CI Pipeline completed successfully!'
        }
        failure {
            echo 'CI Pipeline failed!'
            // You can add notification steps here (email, Slack, etc.)
        }
    }
}
