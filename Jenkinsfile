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
          sh '''
            #— Verify docker CLI is available
            if ! command -v docker >/dev/null 2>&1; then
              echo "ERROR: docker not found in PATH"
              exit 1
            fi

            #— Verify Compose v2 plugin is available
            if ! docker compose version >/dev/null 2>&1; then
              echo "ERROR: docker compose plugin not available"
              exit 1
            fi

            #— Build & run
            docker compose \
              --project-name "$COMPOSE_PROJECT_NAME" \
              --file docker-compose.yml \
              up --build -d
          '''
        }
      }
    }
  }

  post {
    always {
      sh '''
        #— Tear down (ignore errors)
        docker compose \
          --project-name "$COMPOSE_PROJECT_NAME" \
          --file docker-compose.yml \
          down || true
      '''
      echo "✅ Pipeline completed!"
    }
  }
}
