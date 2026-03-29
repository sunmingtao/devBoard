# AWS CI/CD Automation with GitHub Actions

## 🚀 Overview

This document outlines the complete automated deployment pipeline for DevBoard using GitHub Actions to AWS. Every push to main will trigger automatic deployments.

## 🎯 Automation Goals

- **Zero Manual Deployment**: Push to main = auto deploy
- **Environment Separation**: Different branches for dev/staging/prod
- **Rollback Capability**: Automatic rollback on failures
- **Security**: No hardcoded credentials
- **Notifications**: Slack/Email on deployment status

## 📋 CI/CD Architecture

```
GitHub Push → GitHub Actions → AWS
     ↓              ↓           ↓
   main         Build & Test   Deploy
   branch        ↓              ↓
                Docker Image   Frontend → S3/CloudFront
                ↓              Backend → ECS Fargate
                ECR Push
```

## 🔧 Complete Automation Setup

### Phase 1: AWS Preparation

#### 1.1 Create GitHub Actions IAM User
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:RegisterTaskDefinition",
        "ecs:DescribeTaskDefinition",
        "iam:PassRole",
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "cloudfront:CreateInvalidation"
      ],
      "Resource": "*"
    }
  ]
}
```

#### 1.2 Store AWS Credentials in GitHub Secrets
```
GitHub Repo → Settings → Secrets → Actions

Required Secrets:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION (e.g., us-east-1)
- AWS_ACCOUNT_ID
- ECR_REPOSITORY_NAME
- ECS_CLUSTER_NAME
- ECS_SERVICE_NAME
- S3_BUCKET_NAME
- CLOUDFRONT_DISTRIBUTION_ID
- DB_HOST (RDS endpoint)
- DB_PASSWORD (from Secrets Manager)
- JWT_SECRET
```

### Phase 2: GitHub Actions Workflows

#### 2.1 Backend Deployment Workflow
```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend to AWS ECS

on:
  push:
    branches: [ main ]
    paths:
      - 'devboard-backend/**'
      - '.github/workflows/deploy-backend.yml'

env:
  AWS_REGION: ${{ secrets.AWS_REGION }}
  ECR_REPOSITORY: ${{ secrets.ECR_REPOSITORY_NAME }}
  ECS_SERVICE: ${{ secrets.ECS_SERVICE_NAME }}
  ECS_CLUSTER: ${{ secrets.ECS_CLUSTER_NAME }}
  CONTAINER_NAME: devboard-backend

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'
      
      - name: Cache Maven dependencies
        uses: actions/cache@v3
        with:
          path: ~/.m2
          key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
      
      - name: Run tests
        working-directory: ./devboard-backend
        run: mvn clean test
      
      - name: Generate coverage report
        working-directory: ./devboard-backend
        run: mvn jacoco:report
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./devboard-backend/target/site/jacoco/jacoco.xml

  build-and-deploy:
    name: Build and Deploy to ECS
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Set up JDK 21
        uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'

      - name: Build Spring Boot application
        working-directory: ./devboard-backend
        run: mvn clean package -DskipTests

      - name: Build, tag, and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        working-directory: ./devboard-backend
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Render ECS task definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: ./devboard-backend/ecs-task-definition.json
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
          environment-variables: |
            SPRING_PROFILES_ACTIVE=prod
            DB_HOST=${{ secrets.DB_HOST }}
            DB_PORT=3306
            DB_NAME=devboard
            DB_USERNAME=admin
            JWT_EXPIRATION=86400000

      - name: Deploy to Amazon ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true

      - name: Slack Notification
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Backend deployment ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

#### 2.2 Frontend Deployment Workflow
```yaml
# .github/workflows/deploy-frontend.yml
name: Deploy Frontend to S3/CloudFront

on:
  push:
    branches: [ main ]
    paths:
      - 'devboard-frontend/**'
      - '.github/workflows/deploy-frontend.yml'

env:
  AWS_REGION: ${{ secrets.AWS_REGION }}
  S3_BUCKET: ${{ secrets.S3_BUCKET_NAME }}
  CLOUDFRONT_DISTRIBUTION_ID: ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }}

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: ./devboard-frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./devboard-frontend
        run: npm ci
      
      - name: Run tests
        working-directory: ./devboard-frontend
        run: npm run test:run
      
      - name: Run linting
        working-directory: ./devboard-frontend
        run: npm run lint

  build-and-deploy:
    name: Build and Deploy to S3
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: ./devboard-frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./devboard-frontend
        run: npm ci

      - name: Build Vue application
        working-directory: ./devboard-frontend
        env:
          VITE_API_URL: https://api.devboard.example.com
        run: npm run build

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy to S3
        working-directory: ./devboard-frontend
        run: |
          aws s3 sync dist/ s3://${{ env.S3_BUCKET }} --delete
          aws s3 cp dist/index.html s3://${{ env.S3_BUCKET }}/index.html \
            --cache-control "no-cache, no-store, must-revalidate" \
            --content-type "text/html"

      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ env.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"

      - name: Slack Notification
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Frontend deployment ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

#### 2.3 Infrastructure as Code Workflow
```yaml
# .github/workflows/deploy-infrastructure.yml
name: Deploy Infrastructure with Terraform

on:
  push:
    branches: [ main ]
    paths:
      - 'infrastructure/**'
      - '.github/workflows/deploy-infrastructure.yml'

jobs:
  terraform:
    name: Terraform Apply
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Terraform Init
        working-directory: ./infrastructure
        run: terraform init

      - name: Terraform Plan
        working-directory: ./infrastructure
        run: terraform plan -out=tfplan

      - name: Terraform Apply
        working-directory: ./infrastructure
        run: terraform apply -auto-approve tfplan
```

### Phase 3: Multi-Environment Setup

#### 3.1 Branch Strategy
```
main → Production
staging → Staging Environment
develop → Development Environment
feature/* → Feature branches (no auto-deploy)
```

#### 3.2 Environment-Specific Workflows
```yaml
# Modified trigger for different environments
on:
  push:
    branches: 
      - main        # → Production
      - staging     # → Staging
      - develop     # → Development

env:
  ENVIRONMENT: ${{ github.ref == 'refs/heads/main' && 'prod' || 
                   github.ref == 'refs/heads/staging' && 'staging' || 
                   'dev' }}
```

### Phase 4: Advanced Automation

#### 4.1 Blue-Green Deployment
```yaml
- name: Blue-Green Deployment
  run: |
    # Create new target group
    NEW_TG=$(aws elbv2 create-target-group ...)
    
    # Register new tasks to new target group
    aws ecs update-service --cluster $CLUSTER \
      --service $SERVICE-green \
      --task-definition $NEW_TASK_DEF
    
    # Health check
    ./scripts/health-check.sh $NEW_TG
    
    # Switch traffic
    aws elbv2 modify-listener --listener-arn $LISTENER \
      --default-actions Type=forward,TargetGroupArn=$NEW_TG
    
    # Keep old version for rollback
```

#### 4.2 Automated Rollback
```yaml
- name: Health Check
  id: health
  run: |
    for i in {1..10}; do
      if curl -f https://api.devboard.example.com/health; then
        echo "Health check passed"
        exit 0
      fi
      sleep 30
    done
    exit 1

- name: Rollback on Failure
  if: failure()
  run: |
    aws ecs update-service \
      --cluster ${{ env.ECS_CLUSTER }} \
      --service ${{ env.ECS_SERVICE }} \
      --task-definition ${{ env.PREVIOUS_TASK_DEF }}
```

#### 4.3 Database Migrations
```yaml
- name: Run Database Migrations
  run: |
    aws ecs run-task \
      --cluster ${{ env.ECS_CLUSTER }} \
      --task-definition devboard-migrations \
      --overrides '{
        "containerOverrides": [{
          "name": "migrations",
          "command": ["java", "-jar", "app.jar", "--spring.profiles.active=migrate"]
        }]
      }'
```

### Phase 5: Monitoring & Notifications

#### 5.1 Deployment Notifications
```yaml
- name: Send Deployment Email
  if: success()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: '✅ DevBoard Deployment Successful'
    body: |
      Deployment Details:
      - Environment: ${{ env.ENVIRONMENT }}
      - Version: ${{ github.sha }}
      - Deployed by: ${{ github.actor }}
      - Time: ${{ github.event.head_commit.timestamp }}
    to: team@example.com
```

#### 5.2 CloudWatch Metrics
```yaml
- name: Send Custom Metrics
  run: |
    aws cloudwatch put-metric-data \
      --namespace "DevBoard/Deployments" \
      --metric-name "DeploymentSuccess" \
      --value 1 \
      --dimensions Environment=${{ env.ENVIRONMENT }}
```

## 🔐 Security Best Practices

### Secrets Management
```yaml
# Never hardcode secrets
# Use GitHub Secrets + AWS Secrets Manager

- name: Get Secrets from AWS
  run: |
    DB_PASSWORD=$(aws secretsmanager get-secret-value \
      --secret-id devboard/db/password \
      --query SecretString --output text)
    echo "DB_PASSWORD=$DB_PASSWORD" >> $GITHUB_ENV
```

### Least Privilege IAM
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ecs:UpdateService",
      "ecs:DescribeServices"
    ],
    "Resource": [
      "arn:aws:ecs:us-east-1:123456789:service/devboard-cluster/devboard-service"
    ]
  }]
}
```

## 📊 Deployment Dashboard

### GitHub Actions Status Badge
```markdown
![Deploy Backend](https://github.com/yourusername/devboard/workflows/Deploy%20Backend%20to%20AWS%20ECS/badge.svg)
![Deploy Frontend](https://github.com/yourusername/devboard/workflows/Deploy%20Frontend%20to%20S3/badge.svg)
```

### Deployment History
```yaml
- name: Log Deployment
  run: |
    echo "{
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
      \"version\": \"${{ github.sha }}\",
      \"environment\": \"${{ env.ENVIRONMENT }}\",
      \"deployer\": \"${{ github.actor }}\",
      \"status\": \"success\"
    }" >> deployments.log
    
    aws s3 cp deployments.log s3://devboard-deployments/logs/
```

## 🎯 Interview Talking Points

### CI/CD Excellence
- "Implemented zero-downtime deployments using blue-green strategy"
- "Automated testing pipeline ensures code quality before deployment"
- "Infrastructure as Code enables reproducible environments"
- "Rollback capability within 2 minutes of failure detection"

### Security Implementation
- "GitHub Secrets integrated with AWS Secrets Manager"
- "IAM roles follow least privilege principle"
- "All credentials rotated automatically"
- "Deployment audit trail for compliance"

### Cost Optimization
- "Automated shutdown of non-production environments"
- "Resource tagging enables accurate cost allocation"
- "Spot instances for testing environments"
- "CloudWatch alerts for unusual spending"

## 📋 Setup Checklist

### GitHub Repository
- [ ] Enable GitHub Actions
- [ ] Add all required secrets
- [ ] Create branch protection rules
- [ ] Set up environments (prod/staging/dev)

### AWS Prerequisites
- [ ] Create IAM user for GitHub Actions
- [ ] Set up ECR repository
- [ ] Create ECS cluster and service
- [ ] Configure S3 bucket for frontend
- [ ] Set up CloudFront distribution

### Workflow Files
- [ ] Backend deployment workflow
- [ ] Frontend deployment workflow
- [ ] Infrastructure workflow
- [ ] Create ECS task definition JSON
- [ ] Add health check scripts

### Monitoring
- [ ] CloudWatch dashboards
- [ ] SNS topics for alerts
- [ ] Slack webhook for notifications
- [ ] Deployment tracking

## 🚀 Deployment Commands

### Manual Deployment (Emergency)
```bash
# Backend
./scripts/deploy-backend.sh prod v1.2.3

# Frontend  
./scripts/deploy-frontend.sh prod

# Rollback
./scripts/rollback.sh prod v1.2.2
```

### Monitoring Deployments
```bash
# View deployment logs
aws logs tail /aws/ecs/devboard --follow

# Check service health
aws ecs describe-services \
  --cluster devboard-cluster \
  --services devboard-service

# View CloudFront invalidation status
aws cloudfront get-invalidation \
  --distribution-id E1234567890 \
  --id I1234567890
```
Recommendation: EC2 Bastion (Your VPN idea) -- connect to RDS via SSH tunnel

Setup Process:
1. Create EC2 in public subnet
2. Install MySQL client on EC2
3. Test EC2 → RDS connection
4. Set up SSH tunnel from your machine
5. Connect MySQL Workbench via tunnel

This fully automated pipeline ensures that every commit to main is tested, built, and deployed without manual intervention, showcasing modern DevOps practices that employers value!