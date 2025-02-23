pipeline {
    agent {
        docker {
            image 'python:3.10'  
            args '--user root'   
        }
    }
    stages {
        stage('Build') {
            steps {
                sh 'echo "Compiling the code..."'
                sh 'python test.py > errors.txt 2>&1 || true'
            }
        }
        stage('Auto-Fix') {
            steps {
                sh 'pip install openai'
                sh 'python autoRepair.py'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'errors.txt', allowEmptyArchive: true
        }
    }
}