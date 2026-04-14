resource "aws_security_group" "rds_sg" {
  name        = "${var.db_instance_identifier}-sg"
  description = "Security group for ${var.db_instance_identifier}"
  vpc_id      = var.vpc_id

  ingress {
    description     = "MySQL from app VM"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [var.app_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_db_subnet_group" "this" {
  name       = "${var.db_instance_identifier}-subnet-group"
  subnet_ids = var.subnet_ids

  tags = merge(
    local.common_tags,
    {
      Name = "${var.db_instance_identifier}-subnet-group"
    }
  )
}

resource "aws_db_instance" "this" {
  identifier              = var.db_instance_identifier
  engine                  = "mysql"
  engine_version          = var.engine_version
  instance_class          = var.instance_class
  allocated_storage       = var.allocated_storage
  max_allocated_storage   = var.max_allocated_storage
  storage_type            = "gp3"

  db_name  = var.db_name
  username = var.username
  password = var.password
  port     = 3306

  publicly_accessible    = false
  multi_az               = var.multi_az
  deletion_protection    = var.deletion_protection
  skip_final_snapshot    = var.skip_final_snapshot
  backup_retention_period = var.backup_retention_period

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  apply_immediately = true

  tags = merge(
    local.common_tags,
    {
      Name = var.db_instance_identifier
    }
  )
}

locals {
  common_tags = merge(
    {
      Project     = "DevBoard"
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}