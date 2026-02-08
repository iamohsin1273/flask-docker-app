pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t flask-multistage-app .'
            }
        }

        stage('Stop Old Containers') {
            steps {
                sh 'docker rm -f flask-app postgres-db nginx || true'
            }
        }

        stage('Create Network') {
            steps {
                sh 'docker network create flask-network || true'
            }
        }

        stage('Run Postgres') {
            steps {
                sh '''
                docker run -d --name postgres-db \
                  --network flask-network \
                  -e POSTGRES_USER=admin \
                  -e POSTGRES_PASSWORD=secret \
                  -e POSTGRES_DB=flaskdb \
                  -v postgres-data:/var/lib/postgresql/data \
                  postgres:15 || true
                '''
            }
        }

        stage('Run Flask App') {
            steps {
                sh '''
                docker run -d --name flask-app \
                  --network flask-network \
                  -p 5000:5000 \
                  flask-multistage-app || true
                '''
            }
        }

        stage('Run Nginx') {
            steps {
                sh '''
                docker run -d --name nginx \
                  --network flask-network \
                  -p 80:80 \
                  nginx || true
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh 'docker ps'
            }
        }
    }
}
