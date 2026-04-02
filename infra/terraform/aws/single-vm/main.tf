locals {
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

data "aws_ssm_parameter" "al2023_x86_64_ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc"
  })
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-subnet"
  })
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-igw"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-rt"
  })
}

resource "aws_route" "default_ipv4_route" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "ec2" {
  name        = "${local.name_prefix}-ec2-sg"
  description = "Security group for DevBoard EC2"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_ingress_cidr]
  }

  ingress {
    description = "Frontend HTTP"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = var.app_ingress_cidrs
  }

  ingress {
    description = "Backend HTTP"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = var.app_ingress_cidrs
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ec2-sg"
  })
}

resource "aws_key_pair" "devboard_key" {
  key_name   = var.key_name
  public_key = var.public_key

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-key"
  })
}

resource "aws_instance" "devboard" {
  ami                         = data.aws_ssm_parameter.al2023_x86_64_ami.value
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.ec2.id]
  key_name                    = aws_key_pair.devboard_key.key_name
  associate_public_ip_address = true

  user_data = <<-EOF
              #!/bin/bash
              set -eux

              dnf update -y
              dnf install -y docker

              systemctl enable docker
              systemctl start docker

              usermod -aG docker ec2-user

              # Install Docker Compose v2 plugin
              mkdir -p /usr/libexec/docker/cli-plugins

              curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
                -o /usr/libexec/docker/cli-plugins/docker-compose

              chmod +x /usr/libexec/docker/cli-plugins/docker-compose

              # Prepare app directory
              mkdir -p /opt/devboard
              chown -R ec2-user:ec2-user /opt/devboard
              EOF

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ec2"
  })
}