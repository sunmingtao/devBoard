# Jenkins Setup Guide for DevBoard

## 🚀 Introduction

This guide shows how to set up Jenkins in Docker as an alternative CI/CD solution for the DevBoard project. While we use GitHub Actions for the main project, understanding Jenkins is valuable for enterprise environments.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Basic understanding of CI/CD concepts
- 4GB+ RAM available for Jenkins
- Port 8080 available

## 🐳 Jenkins Docker Setup

### Option 1: Quick Start with Docker Run

```bash
# Create a network for Jenkins
docker network create jenkins

# Run Jenkins with Docker-in-Docker capability
docker run -d \
  --name jenkins \
  --network jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --restart unless-stopped \
  jenkins/jenkins:lts-jdk21
```

### Option 2: Docker Compose Setup (Recommended)

Create `docker-compose.jenkins.yml`:

```yaml
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:lts-jdk21
    container_name: jenkins
    user: root  # Required for Docker access
    ports:
      - "8080:8080"      # Jenkins web UI
      - "50000:50000"    # Jenkins agent port
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - ./devboard-backend:/workspace/backend
      - ./devboard-frontend:/workspace/frontend
    environment:
      - JENKINS_OPTS=--prefix=/jenkins
      - JAVA_OPTS=-Xmx2048m -Xms1024m
    restart: unless-stopped
    networks:
      - jenkins-network

  # Optional: Jenkins agent for distributed builds
  jenkins-agent:
    image: jenkins/inbound-agent:latest-jdk21
    container_name: jenkins-agent
    environment:
      - JENKINS_URL=http://jenkins:8080
      - JENKINS_AGENT_WORKDIR=/home/jenkins/agent
    volumes:
      - jenkins_agent_home:/home/jenkins/agent
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - jenkins-network
    depends_on:
      - jenkins

volumes:
  jenkins_home:
    driver: local
  jenkins_agent_home:
    driver: local

networks:
  jenkins-network:
    driver: bridge
```

Start Jenkins:
```bash
docker compose -f docker-compose.jenkins.yml up -d
```

## 🔧 Initial Jenkins Configuration

### 1. Get Initial Admin Password

```bash
# Wait for Jenkins to start (check logs)
docker logs -f jenkins

# Get the initial password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 2. Access Jenkins

1. Open browser: `http://localhost:8080`
2. Enter the initial admin password
3. Install suggested plugins
4. Create admin user
5. Configure Jenkins URL: `http://localhost:8080/`

### 3. Install Required Plugins

Go to **Manage Jenkins** → **Manage Plugins** → **Available**

Install these plugins:
- Docker Pipeline
- Docker
- Pipeline
- Git
- Maven Integration
- NodeJS
- Blue Ocean (modern UI)
- GitHub Integration

## 📝 Creating Jenkins Pipelines

### Backend Pipeline

Create `Jenkinsfile` in `devboard-backend/`:

```groovy
pipeline {
    agent any
    
    tools {
        maven 'Maven-3.9.6'  // Configure in Global Tool Configuration
        jdk 'JDK-21'         // Configure in Global Tool Configuration
    }
    
    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/yourusername/devboard-backend"
        MAVEN_OPTS = '-Xmx3072m'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Building branch: ${env.BRANCH_NAME}"
            }
        }
        
        stage('Build') {
            steps {
                dir('devboard-backend') {
                    sh 'mvn clean compile'
                }
            }
        }
        
        stage('Test') {
            steps {
                dir('devboard-backend') {
                    sh 'mvn test'
                }
            }
            post {
                always {
                    junit 'devboard-backend/target/surefire-reports/*.xml'
                }
            }
        }
        
        stage('Package') {
            steps {
                dir('devboard-backend') {
                    sh 'mvn package -DskipTests'
                }
            }
            post {
                success {
                    archiveArtifacts artifacts: 'devboard-backend/target/*.jar', 
                                     fingerprint: true
                }
            }
        }
        
        stage('Docker Build') {
            when {
                branch 'main'
            }
            steps {
                dir('devboard-backend') {
                    script {
                        docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                    }
                }
            }
        }
        
        stage('Docker Push') {
            when {
                branch 'main'
                expression { 
                    return env.DOCKER_CREDENTIALS_ID != null 
                }
            }
            steps {
                script {
                    docker.withRegistry('', env.DOCKER_CREDENTIALS_ID) {
                        docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}").push()
                        docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}").push('latest')
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
            // Send notification (email, Slack, etc.)
        }
    }
}
```

### Frontend Pipeline

Create `Jenkinsfile` in `devboard-frontend/`:

```groovy
pipeline {
    agent any
    
    tools {
        nodejs 'NodeJS-18'  // Configure in Global Tool Configuration
    }
    
    environment {
        CI = 'true'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                dir('devboard-frontend') {
                    sh 'npm ci'
                }
            }
        }
        
        stage('Lint') {
            steps {
                dir('devboard-frontend') {
                    sh 'npm run lint || true'  // Don't fail on lint warnings
                }
            }
        }
        
        stage('Build') {
            steps {
                dir('devboard-frontend') {
                    sh 'npm run build'
                }
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                dir('devboard-frontend') {
                    archiveArtifacts artifacts: 'dist/**/*', 
                                     fingerprint: true
                }
            }
        }
        
        stage('Docker Build') {
            when {
                branch 'main'
            }
            steps {
                dir('devboard-frontend') {
                    script {
                        docker.build("devboard-frontend:${BUILD_NUMBER}")
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

## 🔄 Creating Pipeline Jobs

### Method 1: Classic Pipeline Job

1. Click **New Item**
2. Enter name: `devboard-backend-pipeline`
3. Select **Pipeline**
4. Under Pipeline section:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `file:///workspace/backend` (or your Git URL)
   - Script Path: `Jenkinsfile`
5. Save and Build

### Method 2: Multibranch Pipeline (Recommended)

1. Click **New Item**
2. Enter name: `devboard-multibranch`
3. Select **Multibranch Pipeline**
4. Branch Sources:
   - Add source → Git
   - Project Repository: Your Git URL
   - Credentials: Add if needed
5. Build Configuration:
   - Mode: by Jenkinsfile
   - Script Path: `Jenkinsfile`
6. Scan Multibranch Pipeline Triggers:
   - Check "Periodically if not otherwise run"
   - Interval: 1 minute
7. Save

### Method 3: Blue Ocean (Modern UI)

1. Open Blue Ocean: `http://localhost:8080/blue`
2. Click **Create a new Pipeline**
3. Select where code is stored (Git, GitHub, etc.)
4. Connect and select repository
5. Blue Ocean auto-detects Jenkinsfile

## 🛠️ Global Tool Configuration

Go to **Manage Jenkins** → **Global Tool Configuration**

### Maven Configuration
```
Name: Maven-3.9.6
Install automatically: ✓
Version: 3.9.6
```

### JDK Configuration
```
Name: JDK-21
Install automatically: ✓
Version: jdk-21
```

### NodeJS Configuration
```
Name: NodeJS-18
Install automatically: ✓
Version: 18.20.2
Global npm packages: (leave empty)
```

### Docker Configuration
```
Name: Docker
Install automatically: ✓
Docker version: latest
```

## 🔐 Credentials Management

Go to **Manage Jenkins** → **Manage Credentials**

### Add Docker Hub Credentials
1. Click **(global)** → **Add Credentials**
2. Kind: **Username with password**
3. Username: Your Docker Hub username
4. Password: Your Docker Hub token
5. ID: `dockerhub-credentials`
6. Description: Docker Hub Access

### Add GitHub Credentials (if private repo)
1. Kind: **Username with password** (or SSH key)
2. Username: Your GitHub username
3. Password: Personal Access Token
4. ID: `github-credentials`

## 🎯 Advanced Features

### 1. Parallel Stages

```groovy
stage('Parallel Tests') {
    parallel {
        stage('Unit Tests') {
            steps {
                sh 'mvn test -Dtest=*UnitTest'
            }
        }
        stage('Integration Tests') {
            steps {
                sh 'mvn test -Dtest=*IntegrationTest'
            }
        }
    }
}
```

### 2. Environment-Specific Builds

```groovy
stage('Deploy') {
    when {
        branch 'main'
    }
    steps {
        script {
            if (env.BRANCH_NAME == 'main') {
                env.DEPLOY_ENV = 'production'
            } else if (env.BRANCH_NAME == 'develop') {
                env.DEPLOY_ENV = 'staging'
            }
            
            sh "deploy.sh ${env.DEPLOY_ENV}"
        }
    }
}
```

### 3. Notifications

```groovy
post {
    success {
        emailext (
            subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
            body: "Good news! Build succeeded.",
            to: 'team@example.com'
        )
    }
    failure {
        slackSend (
            color: 'danger',
            message: "Build Failed: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
        )
    }
}
```

## 📊 Jenkins vs GitHub Actions Comparison

| Feature | Jenkins | GitHub Actions |
|---------|---------|----------------|
| **Setup Time** | 30-60 minutes | 5 minutes |
| **Maintenance** | Regular updates needed | Zero maintenance |
| **Cost** | Free (your resources) | 2000 free minutes/month |
| **Flexibility** | Extremely flexible | Limited to GitHub |
| **Plugins** | 1000+ plugins | Marketplace actions |
| **Learning Curve** | Steeper | Easier |
| **Enterprise Use** | Very common | Growing |

## 🚀 Tips for Success

1. **Start Simple**: Get basic pipeline working first
2. **Use Blue Ocean**: Modern UI is easier to understand
3. **Version Control**: Always use Jenkinsfile in repo
4. **Use Declarative**: Easier than Scripted Pipeline
5. **Test Locally**: Use `docker exec` to test commands
6. **Monitor Resources**: Jenkins can be memory hungry

## 🛑 Troubleshooting

### Common Issues

1. **Permission Denied for Docker**
   ```bash
   docker exec -u root jenkins chmod 666 /var/run/docker.sock
   ```

2. **Out of Memory**
   - Increase JAVA_OPTS memory
   - Reduce concurrent builds

3. **Can't Find Tools**
   - Check Global Tool Configuration
   - Ensure tools are installed

4. **Workspace Issues**
   - Use `cleanWs()` in post section
   - Check disk space

## 📚 Learning Resources

1. **Official Jenkins Documentation**
   - https://www.jenkins.io/doc/

2. **Pipeline Syntax Reference**
   - https://www.jenkins.io/doc/book/pipeline/syntax/

3. **Best Practices**
   - https://www.jenkins.io/doc/book/pipeline/pipeline-best-practices/

4. **Example Pipelines**
   - https://github.com/jenkinsci/pipeline-examples

## 🎉 Conclusion

Jenkins provides powerful CI/CD capabilities with complete control. While it requires more setup than GitHub Actions, it offers:

- Unlimited build minutes
- Complete customization
- Enterprise-grade features
- On-premise deployment

For learning and enterprise preparation, Jenkins knowledge is invaluable. For modern cloud projects, GitHub Actions is often more practical.

Both are excellent tools - choose based on your needs!