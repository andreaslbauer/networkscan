// Jenkinsfile to build networkscan python file and create Docker container
// Useful information:  https://dzone.com/articles/dockerizing-jenkins-2-setup-and-using-it-along-wit

pipeline {
    agent any

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
            // build the docker image from the source code using the BUILD_ID parameter in image name
            sh "docker build -t networkscan-${BUILD_ID} ."
        }
    }
}
