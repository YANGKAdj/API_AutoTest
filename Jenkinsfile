pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t api-autotest:latest .'
            }
        }

        stage('Run Tests with docker-compose') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker-compose up --abort-on-container-exit --build'
            }
        }
    }

    post {
        always {
            sh 'docker-compose down || true'
        }
    }
}

