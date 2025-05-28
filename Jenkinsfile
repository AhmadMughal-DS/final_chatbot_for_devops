pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "jenkins_chatbot"
    // Ensure Jenkins can see docker-compose in /usr/local/bin
    PATH = "/usr/local/bin:${env.PATH}"
  }

  stages {
    stage('Checkout SCM') {
      steps {
        // Pull your Jenkinsfile & code
        checkout scm
      }
    }

    stage('Build and Run App') {
      steps {
        // Fail if takes longer than 100 minutes
        timeout(time: 100, unit: 'MINUTES') {
          // Run docker-compose with project name
          sh """
            docker-compose -p "$COMPOSE_PROJECT_NAME" -f docker-compose.yml up --build -d
          """
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
