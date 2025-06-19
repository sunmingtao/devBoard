# AWS Resources for DevBoard

## Account Information
- **Account ID**: 627073650332
- **IAM User**: smt-admin
- **Region**: us-east-1

## Created Resources

### S3 Bucket (Frontend)
- **Bucket Name**: devboard-frontend-627073650332
- **Purpose**: Static website hosting for Vue.js frontend
- **Configuration**: Website hosting enabled
- **URL**: http://devboard-frontend-627073650332.s3-website-us-east-1.amazonaws.com

### ECR Repository (Backend)
- **Repository Name**: devboard-backend
- **Repository URI**: 627073650332.dkr.ecr.us-east-1.amazonaws.com/devboard-backend
- **Purpose**: Store Docker images for Spring Boot backend

### SNS Topic (Billing Alerts)
- **Topic Name**: billing-alerts
- **Topic ARN**: arn:aws:sns:us-east-1:627073650332:billing-alerts
- **Purpose**: Email notifications for billing thresholds

## Next Steps
1. Set up CloudFront distribution for S3
2. Create VPC and networking
3. Set up RDS MySQL database
4. Create ECS cluster and service
5. Configure Application Load Balancer

## GitHub Secrets Required
```
AWS_ACCESS_KEY_ID: [Your IAM Access Key]
AWS_SECRET_ACCESS_KEY: [Your IAM Secret Key]
AWS_REGION: us-east-1
AWS_ACCOUNT_ID: 627073650332
ECR_REPOSITORY_URI: 627073650332.dkr.ecr.us-east-1.amazonaws.com/devboard-backend
S3_BUCKET_NAME: devboard-frontend-627073650332
```

## CloudFront
- Distribution ID: E13IQLG4XH9EXL
- CloudFront URL: https://d58an524la6th.cloudfront.net
- Status: Deployed

## RDS MySQL
- Instance Identifier: devboard-mysql
- Endpoint: devboard-mysql.cgt0u0gesgx3.us-east-1.rds.amazonaws.com
- Port: 3306
- Instance Class: db.t3.micro (Free Tier)

## ECS Fargate
- Cluster: devboard-cluster
- Service: devboard-backend-service
- Task Definition: devboard-backend:1
- Status: Running

## Cost Monitoring
- Billing alerts configured for $10, $50, $100 thresholds
- SNS notifications to email address
- Regular monitoring recommended
