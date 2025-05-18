pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = "jenkins_chatbot"
    }

    stages {
        stage('Clone Code') {
            steps {
                git 'https://github.com/AhmadMughal-DS/final_chatbot_for_devops.git'
            }
        }

        stage('Build and Run App') {
            steps {
                sh 'docker-compose -p $COMPOSE_PROJECT_NAME -f docker-compose.yml up --build -d'
            }
        }
    }

    post {
        always {
            echo "✅ Pipeline completed!"
        }
    }
}
