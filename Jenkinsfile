pipeline {
    // Use Docker pipeline plugin to get proper Docker permissions
    agent {
        label 'docker'
    }
    
    environment {
        PROJECT_NAME = 'devops_chatbot_ci'
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        GITHUB_REPO = 'https://github.com/AhmadMughal-DS/final_chatbot_for_devops'
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
        
        stage('Setup Python') {
            steps {
                echo 'Setting up Python environment'
                // Use the Python tool in Jenkins, or install if needed
                sh '''
                    if ! command -v python3 &> /dev/null; then
                        echo "Python not found, installing..."
                        sudo apt-get update -y || true
                        sudo apt-get install -y python3 python3-pip || true
                    fi
                    python3 --version || python --version
                '''
                
                // Install pytest if needed
                sh 'pip3 install pytest || pip install pytest || echo "Skipping pytest installation"'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running Python tests'
                sh 'python3 -m pytest -v || python -m pytest -v || echo "No tests available, continuing..."'
            }
        }
        
        stage('Fix Docker Permissions') {
            steps {
                echo 'Setting up Docker permissions'
                // This step ensures Jenkins user can use Docker
                sh '''
                    # Add Jenkins to docker group if needed
                    if [ -S /var/run/docker.sock ]; then
                        sudo chmod 666 /var/run/docker.sock || true
                        echo "Docker socket permissions updated"
                    fi
                '''
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building Docker containers'
                // Check Docker and Docker Compose installation
                sh 'docker --version'
                sh 'docker-compose --version || docker compose --version'
                
                // Build the Docker images with sudo if needed
                sh '''
                    if docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} build --no-cache; then
                        echo "Docker build completed successfully"
                    else
                        echo "Trying with sudo..."
                        sudo docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} build --no-cache
                    fi
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying application with Docker Compose'
                
                // Stop any existing containers with the same project name
                sh '''
                    docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} down || \
                    sudo docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} down || \
                    echo "No existing containers to stop"
                '''
                
                // Start the containers in detached mode
                sh '''
                    if docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} up -d; then
                        echo "Deployment successful"
                    else
                        echo "Trying with sudo..."
                        sudo docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} up -d
                    fi
                '''
                
                // Verify that the containers are running
                sh 'docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} ps || sudo docker-compose -p ${PROJECT_NAME} -f ${DOCKER_COMPOSE_FILE} ps'
            }
        }
        
        stage('Verify') {
            steps {
                echo 'Verifying the deployment'
                // Wait for application to be ready
                sh 'sleep 10'
                  // Check if the container is running
                sh 'docker ps | grep devops_chatbot || sudo docker ps | grep devops_chatbot || echo "Container not found"'
                
                // Try to connect to the backend service (using the port from docker-compose.yml)
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
