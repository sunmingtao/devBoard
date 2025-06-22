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
      image = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/devboard-backend:latest"
      
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
          name  = "DB_HOST"
          value = aws_db_instance.dev_mysql.address
        },
        {
          name  = "DB_PORT"
          value = tostring(aws_db_instance.dev_mysql.port)
        },
        {
          name  = "DB_NAME"
          value = "devboard"
        },
        {
          name  = "DB_USERNAME"
          value = "admin"
        },
        {
          name  = "DB_PASSWORD"
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
        command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
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

# Frontend Task Definition
resource "aws_ecs_task_definition" "dev_frontend" {
  family                   = "${var.project_name}-${var.environment}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.dev_ecs_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "frontend"
      image = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/devboard-frontend:latest"
      
      portMappings = [
        {
          containerPort = 5173
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "VITE_API_BASE_URL"
          value = "http://${aws_lb.dev_alb.dns_name}/api"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.project_name}-${var.environment}-frontend"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:5173/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-frontend-task"
    Environment = var.environment
    Project     = var.project_name
  }
}

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

# Frontend Service
resource "aws_ecs_service" "dev_frontend" {
  name            = "${var.project_name}-${var.environment}-frontend"
  cluster         = aws_ecs_cluster.dev_cluster.id
  task_definition = aws_ecs_task_definition.dev_frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
    security_groups  = [aws_security_group.dev_ecs_sg.id]
    assign_public_ip = true  # Needed for Fargate to pull images
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.dev_frontend_tg.arn
    container_name   = "frontend"
    container_port   = 5173
  }

  depends_on = [
    aws_lb_listener.dev_alb_listener
  ]

  tags = {
    Name        = "${var.project_name}-${var.environment}-frontend-service"
    Environment = var.environment
    Project     = var.project_name
  }
}

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

resource "aws_cloudwatch_log_group" "frontend_logs" {
  name              = "/ecs/${var.project_name}-${var.environment}-frontend"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-${var.environment}-frontend-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}