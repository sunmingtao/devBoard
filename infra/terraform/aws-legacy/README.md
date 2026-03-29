# DevBoard Development Environment - Terraform

This Terraform configuration creates a complete development environment for DevBoard with its own isolated infrastructure.

## Architecture

- **VPC**: 10.1.0.0/16 (separate from production)
- **Public Subnets**: 10.1.1.0/24, 10.1.2.0/24 (for ALB, NAT Gateway)
- **Private Subnets**: 10.1.10.0/24, 10.1.11.0/24 (for ECS, RDS, Redis)
- **RDS MySQL**: db.t3.micro with 20GB storage
- **ElastiCache Redis**: cache.t3.micro single-node cluster
- **ECS Cluster**: For running containerized applications
- **Application Load Balancer**: Routes traffic to frontend/backend

## Quick Start

1. **Initialize Terraform**:
   ```bash
   cd terraform
   terraform init
   ```

2. **Plan the deployment**:
   ```bash
   terraform plan
   ```

3. **Apply the configuration**:
   ```bash
   terraform apply
   ```

4. **Get outputs**:
   ```bash
   terraform output
   ```

## Outputs

After deployment, Terraform will output:
- VPC ID
- Subnet IDs  
- RDS endpoint and port
- Redis endpoint and port
- ALB DNS name
- ECS cluster name

## Cost Optimization

This development environment uses cost-optimized resources:
- db.t3.micro for RDS (free tier eligible)
- cache.t3.micro for Redis
- Single AZ deployment
- No Multi-AZ for RDS
- Minimal backup retention

## Cleanup

To destroy the environment:
```bash
terraform destroy
```

## Next Steps

After infrastructure is created:
1. Update ECS task definitions with new RDS/Redis endpoints
2. Deploy applications to the new ECS cluster
3. Update DNS/routing as needed