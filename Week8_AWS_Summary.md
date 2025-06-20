# Week 8 - AWS Deployment Summary

## What We Accomplished

Successfully deployed the full DevBoard application to AWS using multiple services:

### 1. CloudFront CDN Setup
- Created CloudFront distribution with S3 origin
- Configured:
  - 1-hour caching for static assets
  - Gzip compression
  - HTTPS redirect
  - SPA support with custom error pages (404 → index.html)
- Added API proxy behavior for `/api/*` paths to solve HTTPS mixed content issue

### 2. RDS MySQL Database
- Created `db.t3.micro` instance (Free Tier eligible)
- Configured in private subnet with proper security groups
- Enabled automated backups with 7-day retention
- Point-in-time recovery available

### 3. ECS Fargate Deployment
- Created ECS cluster: `devboard-cluster`
- Deployed Spring Boot backend as serverless container
- Configured task definition with RDS environment variables
- Health checks on `/api/hello` endpoint

### 4. Application Load Balancer
- Internet-facing ALB: `devboard-alb`
- Target group with health checks
- Fixed 401 error by using public endpoint for health checks
- Created GitHub issue #17 to document the solution

### 5. Architecture Overview
```
User → CloudFront (HTTPS) → S3 (Frontend)
                         ↘
                           ALB → ECS Fargate → RDS MySQL
```

## Challenges Solved

1. **Docker Platform Mismatch**
   - Error: ARM image incompatible with linux/amd64
   - Solution: Rebuilt with `--platform linux/amd64`

2. **ALB Health Check Failures**
   - Error: 401 Unauthorized on `/`
   - Solution: Used `/api/hello` public endpoint

3. **HTTPS Mixed Content**
   - Error: HTTPS frontend calling HTTP backend
   - Solution: CloudFront API proxy for `/api/*` requests

4. **Frontend CORS Issues**
   - Error: Hardcoded localhost in authService.js
   - Solution: Updated to use environment variables

## Current Status

✅ All components deployed and functional
✅ Registration and login working (except passwords with special characters)
✅ Tasks can be created, updated, and managed
✅ All traffic secured with HTTPS

## Known Issues

1. JSON parsing error with special characters in passwords
2. Cannot directly access RDS from local machine (security best practice)

## AWS Resources Created

- **S3 Bucket**: `devboard-frontend-627073650332`
- **CloudFront**: `https://d58an524la6th.cloudfront.net`
- **ECR Repository**: `devboard-backend`
- **RDS Instance**: `devboard-mysql`
- **ECS Service**: `devboard-backend-alb`
- **ALB**: `devboard-alb-381662016.us-east-1.elb.amazonaws.com`

## Next Steps

1. Set up ElastiCache Redis for session management
2. Configure custom domain names
3. Set up CloudWatch monitoring and alerts
4. Implement auto-scaling policies
5. Add CI/CD pipeline for automated deployments

## Cost Considerations

- Most services using Free Tier (RDS, ECS with limited usage)
- Billing alerts set at $10, $50, $100 thresholds
- Regular monitoring recommended to avoid surprise charges

## Learning Outcomes

- Understanding of AWS service integration
- Experience with containerized deployments
- Troubleshooting complex distributed systems
- Security best practices (private subnets, security groups)
- HTTPS and CORS configuration in cloud environments