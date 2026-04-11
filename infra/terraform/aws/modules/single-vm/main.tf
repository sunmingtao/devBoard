resource "aws_security_group" "vm_sg" {
  name        = "${var.instance_name}-sg"
  description = "Security group for ${var.instance_name}"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]
  }

  ingress {
    description = "App port"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_key_pair" "vm_key" {
  key_name   = "${var.instance_name}-key"
  public_key = var.public_key
}

data "aws_ami" "amazon_linux" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "vm" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.vm_key.key_name
  vpc_security_group_ids      = [aws_security_group.vm_sg.id]
  associate_public_ip_address = var.associate_public_ip_address
  monitoring                  = var.monitoring_enabled
  disable_api_termination     = var.enable_termination_protection

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    app_port = var.app_port
  })

  root_block_device {
    volume_size = var.root_volume_size
  }

  tags = merge(
    local.common_tags,
    {
      Name = var.instance_name
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