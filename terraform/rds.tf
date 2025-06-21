# RDS MySQL Database for Development Environment

# DB Subnet Group
resource "aws_db_subnet_group" "dev_db_subnet_group" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-subnet-group"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Security Group for RDS
resource "aws_security_group" "dev_rds_sg" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Security group for development RDS MySQL instance"
  vpc_id      = aws_vpc.dev_vpc.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.dev_ecs_sg.id]
    description     = "MySQL access from ECS tasks"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-sg"
    Environment = var.environment
    Project     = var.project_name
  }
}

# RDS MySQL Instance
resource "aws_db_instance" "dev_mysql" {
  identifier = "${var.project_name}-${var.environment}-mysql"

  # Engine Configuration
  engine         = "mysql"
  engine_version = "8.0.35"
  instance_class = "db.t3.micro"

  # Storage Configuration
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  # Database Configuration
  db_name  = "devboard"
  username = "admin"
  password = "devboard123!"  # In production, use AWS Secrets Manager

  # Network Configuration
  db_subnet_group_name   = aws_db_subnet_group.dev_db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.dev_rds_sg.id]
  publicly_accessible    = false

  # Backup and Maintenance
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  # Development optimizations
  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name        = "${var.project_name}-${var.environment}-mysql"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.dev_mysql.endpoint
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.dev_mysql.port
}