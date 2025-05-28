pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "jenkins_chatbot"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build & Start') {
      steps {
        timeout(time: 100, unit: 'MINUTES') {
          sh """
            # fail early if docker itself isn't present
            if ! command -v docker &> /dev/null; then
              echo "ERROR: docker not found"
              exit 1
            fi

            # now use the v2 plugin sub-command
            docker compose \
              --project-name "$COMPOSE_PROJECT_NAME" \
              --file docker-compose.yml \
              up --build -d
          """
        }
      }
    }
  }

  post {
    always {
      sh """
        # gracefully tear down; ignore errors
        docker compose \
          --project-name "$COMPOSE_PROJECT_NAME" \
          --file docker-compose.yml \
          down || true
      """
      echo "✅ Pipeline completed!"
    }
  }
}
