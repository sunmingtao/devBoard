variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-2"
}

variable "project_name" {
  description = "Project name used in tags/resource names"
  type        = string
  default     = "devboard"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "availability_zone" {
  description = "Availability zone for the public subnet"
  type        = string
  default     = "ap-southeast-2a"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t4g.small"
}

variable "key_name" {
  description = "EC2 key pair name"
  type        = string
  default     = "devboard-aws"
}

variable "public_key" {
  description = "SSH public key content"
  type        = string
}

variable "private_key_path" {
  description = "Path to private SSH key"
  type        = string
  default     = "~/.ssh/devboard-aws"
}

variable "ssh_ingress_cidr" {
  description = "Your public IP in CIDR format for SSH, e.g. 1.2.3.4/32"
  type        = string
}

variable "app_ingress_cidrs" {
  description = "CIDRs allowed to access app ports"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}