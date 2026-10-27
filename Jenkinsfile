// Declarative pipeline: test, build and deploy the Flask + Nginx + PostgreSQL stack
// with Docker Compose. The Jenkins agent needs Docker with the Compose plugin.
pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }

    environment {
        COMPOSE_PROJECT_NAME = 'flask-docker-app'
    }

    stages {
        stage('Test') {
            steps {
                // Builds the "test" stage of the Dockerfile, which runs pytest.
                sh 'docker build --target test -t flask-app-test .'
            }
        }

        stage('Build') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Deploy') {
            steps {
                // Recreates only the containers whose image or config changed.
                // The postgres-data volume is kept, so database contents survive.
                sh 'docker compose up -d --remove-orphans'
            }
        }

        stage('Smoke Test') {
            steps {
                // Request /health through Nginx from inside the Nginx container,
                // so the check works no matter which host port is published.
                sh '''
                for i in $(seq 1 20); do
                  if docker compose exec -T nginx wget -qO- http://localhost/health; then
                    echo
                    echo "Smoke test passed"
                    exit 0
                  fi
                  echo "Waiting for the stack to become healthy ($i/20)..."
                  sleep 3
                done
                echo "Smoke test failed"
                exit 1
                '''
            }
        }
    }

    post {
        failure {
            sh 'docker compose logs --tail=100 || true'
        }
        always {
            sh 'docker compose ps || true'
        }
    }
}
