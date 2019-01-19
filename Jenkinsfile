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

        stage('Build Docker Container') {
            steps {
                // build the docker image from the source code using the BUILD_ID parameter in image name
                sh "docker build -t andreaslbauer/networkscan ."
            }
        }

        stage('Move to repository') {
            steps {
                // build the docker image from the source code using the BUILD_ID parameter in image name
                sh "pwd"
                sh "ls -lag"
            }
        }

    }
}
