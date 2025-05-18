pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "jenkins_chatbot"
  }

  stages {
    stage('Build and Run App') {
      steps {
        // fail if takes longer than 10 minutes
        timeout(time: 10, unit: 'MINUTES') {
          sh 'docker-compose -p $COMPOSE_PROJECT_NAME -f docker-compose.yml up --build -d'
        }
      }
    }
  }

  post {
    always {
      echo "✅ Pipeline completed!"
    }
  }
}
