# ElastiCache Redis for Development Environment

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "dev_redis_subnet_group" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis-subnet-group"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Security Group for ElastiCache Redis
resource "aws_security_group" "dev_redis_sg" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "Security group for development ElastiCache Redis cluster"
  vpc_id      = aws_vpc.dev_vpc.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.dev_ecs_sg.id]
    description     = "Redis access from ECS tasks"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ElastiCache Redis Cluster
resource "aws_elasticache_replication_group" "dev_redis" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  description                = "Development Redis cluster for DevBoard"

  # Node Configuration
  node_type          = "cache.t3.micro"
  port               = 6379
  parameter_group_name = "default.redis7"

  # Cluster Configuration
  num_cache_clusters = 1
  
  # Network Configuration
  subnet_group_name  = aws_elasticache_subnet_group.dev_redis_subnet_group.name
  security_group_ids = [aws_security_group.dev_redis_sg.id]

  # Backup Configuration
  snapshot_retention_limit = 1
  snapshot_window         = "03:00-05:00"

  # Development optimizations
  auto_minor_version_upgrade = true
  multi_az_enabled          = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-redis"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.dev_redis.primary_endpoint_address
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_replication_group.dev_redis.port
}