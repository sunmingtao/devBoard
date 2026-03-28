pipeline {
    agent any

    parameters {
        string(name: 'VM_IP', defaultValue: '139.180.161.144', description: 'Target VM public IP')
    }

    environment {
        IMAGE_NAME_BACKEND = 'sunmingtao/devboard-backend'
        IMAGE_NAME_FRONTEND = 'sunmingtao/devboard-frontend'
        IMAGE_TAG = "${BUILD_NUMBER}"
        REMOTE_USER = 'root'
    }

    stages {


        stage('Validate Parameters') {
            steps {
                script {
                    if (!params.VM_IP?.trim()) {
                        error("VM_IP parameter is required")
                    }
                }
            }
        }
        
        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    credentialsId: 'devboard-repo',
                    url: 'https://github.com/sunmingtao/devBoard.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t devboard-backend:latest ./devboard-backend'
                sh 'docker build -t devboard-frontend:latest ./devboard-frontend'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                        docker tag devboard-backend:latest ${IMAGE_NAME_BACKEND}:latest
                        docker tag devboard-backend:latest ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME_BACKEND}:latest
                        docker push ${IMAGE_NAME_BACKEND}:${IMAGE_TAG}

                        docker tag devboard-frontend:latest ${IMAGE_NAME_FRONTEND}:latest
                        docker tag devboard-frontend:latest ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME_FRONTEND}:latest
                        docker push ${IMAGE_NAME_FRONTEND}:${IMAGE_TAG}
                    """
                }
            }
        }

        stage('Deploy to VM') {
            steps {
                sshagent(credentials: ['digitalocean-vm-ssh']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${params.VM_IP} 'mkdir -p /opt/devboard'
                        scp -o StrictHostKeyChecking=no docker-compose.yml ${REMOTE_USER}@${params.VM_IP}:/opt/devboard/docker-compose.yml
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${params.VM_IP} '
                            cd /opt/devboard &&
                            cat > .env <<EOF
IMAGE_TAG=${IMAGE_TAG}
EOF
                            docker compose pull &&
                            docker compose up -d
                        '
                    """
                }
            }
        }
    }
}