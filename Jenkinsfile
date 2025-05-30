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

    stage('Verify Deployment') {
      steps {
        script {
          // Wait for application to be fully ready
          sleep(time: 20, unit: 'SECONDS')
          
          // Get the host IP for display purposes
          def hostIP = sh(script: 'curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo "localhost"', returnStdout: true).trim()
          
          // Check if application is accessible
          def statusCode = sh(script: '''
            curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ || echo "failed"
          ''', returnStdout: true).trim()
          
          if (statusCode == "200") {
            echo "✅ Application accessible at http://${hostIP}:8000"
          } else {
            echo "❌ Application not accessible. HTTP status: ${statusCode}"
            error "Application health check failed"
          }
        }
      }
    }
    
    stage('Keep Running') {
      steps {
        // This stage keeps the application running for a specified time
        timeout(time: 120, unit: 'MINUTES') {
          input message: 'Application is running at http://PUBLIC-IP:8000. Click "Proceed" to stop the application or wait for timeout.', ok: 'Stop Application'
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
