pipeline {
    agent none

    stages {
        stage('Build') { 
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
            node {
                // build the docker image from the source code using the BUILD_ID parameter in image name
                sh "docker build -t networkscan-${BUILD_ID} ."
            }
        }
    }
}
