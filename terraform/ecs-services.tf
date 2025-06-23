# ECS Task Definitions and Services for Development Environment

# Backend Task Definition
resource "aws_ecs_task_definition" "dev_backend" {
  family                   = "${var.project_name}-${var.environment}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.dev_ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/devboard-backend:dev-latest"
      
      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "SPRING_PROFILES_ACTIVE"
          value = "mysql"
        },
        {
          name  = "DATABASE_URL"
          value = "jdbc:mysql://${aws_db_instance.dev_mysql.address}:${aws_db_instance.dev_mysql.port}/devboard?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC&createDatabaseIfNotExist=true"
        },
        {
          name  = "DATABASE_USERNAME"
          value = "admin"
        },
        {
          name  = "DATABASE_PASSWORD"
          value = "devboard123!"
        },
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_replication_group.dev_redis.primary_endpoint_address
        },
        {
          name  = "REDIS_PORT"
          value = "6379"
        },
        {
          name  = "CORS_ALLOWED_ORIGINS"
          value = "http://${aws_lb.dev_alb.dns_name},http://localhost:3000,http://localhost:5173"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.project_name}-${var.environment}-backend"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8080/api/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-backend-task"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Frontend Task Definition - REMOVED
# Frontend is now deployed to S3/CloudFront instead of ECS

# Backend Service
resource "aws_ecs_service" "dev_backend" {
  name            = "${var.project_name}-${var.environment}-backend"
  cluster         = aws_ecs_cluster.dev_cluster.id
  task_definition = aws_ecs_task_definition.dev_backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
    security_groups  = [aws_security_group.dev_ecs_sg.id]
    assign_public_ip = true  # Needed for Fargate to pull images
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.dev_backend_tg.arn
    container_name   = "backend"
    container_port   = 8080
  }

  depends_on = [
    aws_lb_listener.dev_alb_listener,
    aws_lb_listener_rule.dev_backend_rule
  ]

  tags = {
    Name        = "${var.project_name}-${var.environment}-backend-service"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Frontend Service - REMOVED
# Frontend is now deployed to S3/CloudFront instead of ECS

# Data source for AWS account ID
data "aws_caller_identity" "current" {}

# CloudWatch Log Groups (optional - ECS can create them automatically)
resource "aws_cloudwatch_log_group" "backend_logs" {
  name              = "/ecs/${var.project_name}-${var.environment}-backend"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-${var.environment}-backend-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Frontend CloudWatch logs removed - using S3/CloudFront instead