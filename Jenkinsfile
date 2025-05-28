pipeline {
  agent any

  environment {
    // your compose project name
    COMPOSE_PROJECT_NAME = "jenkins_chatbot"
    // explicit path to the standalone docker-compose binary
    DOCKER_COMPOSE = '/usr/local/bin/docker-compose'
    // ensure that path is available if you call just "docker-compose"
    PATH = "/usr/local/bin:${env.PATH}"
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
          // use the full path so we never hit "not found"
          sh """
            if [ ! -x "${DOCKER_COMPOSE}" ]; then
              echo "ERROR: ${DOCKER_COMPOSE} not found or not executable"
              exit 1
            fi
            ${DOCKER_COMPOSE} -p "${COMPOSE_PROJECT_NAME}" -f docker-compose.yml up --build -d
          """
        }
      }
    }
  }

  post {
    always {
      // optional cleanup; remove containers if you wish
      sh """
        if [ -x "${DOCKER_COMPOSE}" ]; then
          ${DOCKER_COMPOSE} -p "${COMPOSE_PROJECT_NAME}" -f docker-compose.yml down || true
        fi
      """
      echo "✅ Pipeline completed!"
    }
  }
}
