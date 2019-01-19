// Jenkinsfile to build networkscan python file and create Docker container
// https://dzone.com/refcardz/declarative-pipeline-with-jenkins?chapter=1

pipeline {
    agent any

    stages {
        stage('Build Code') {
            agent {
                docker {
                    image 'python:3-alpine'
                }
            }
            steps {
                sh 'python3 -m py_compile networkscan.py'
            }
        }

        stage('Build Docker') {
            steps {
                // build the docker image from the source code using the BUILD_ID parameter in image name
                sh "docker build -t networkscan-${BUILD_ID} ."
            }
        }
    }
}
