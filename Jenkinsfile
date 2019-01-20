// Jenkinsfile to build networkscan python file and create Docker container
// https://dzone.com/refcardz/declarative-pipeline-with-jenkins?chapter=1
// https://medium.com/@gustavo.guss/jenkins-building-docker-image-and-sending-to-registry-64b84ea45ee9

pipeline {

    environment {
        registry = "andreaslbauer/networkscan"
        registryCredential = 'DockerHub'
        dockerImage = ''
    }

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

        stage('Build Container') {
            steps {
                // build the docker image from the source code using the BUILD_ID parameter in image name
                script {
                    dockerImage = docker.build registry + ":$BUILD_NUMBER"
                    //dockerImage = docker.build registry + ":latest"
                }
            }
        }

        stage('Move to repository') {
            steps {
                // build the docker image from the source code using the BUILD_ID parameter in image name
                script {
                    docker.withRegistry( '', registryCredential ) {
                    dockerImage.push()
                  }
                }
            }
        }

        stage('Remove Unused docker image') {
            steps {
                sh "docker rmi $registry:$BUILD_NUMBER"
                //sh "docker rmi $registry:latest"
            }
        }
    }
}
