variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "instance_name" {
  description = "EC2 instance name"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "app_port" {
  description = "Application port"
  type        = number
}

variable "ssh_allowed_cidr" {
  description = "Allowed CIDR for SSH"
  type        = string
}

variable "public_key_path" {
  description = "Path to SSH public key"
  type        = string
}

variable "root_volume_size" {
  description = "Root EBS volume size"
  type        = number
}

variable "enable_termination_protection" {
  description = "Whether to enable EC2 termination protection"
  type        = bool
}

variable "monitoring_enabled" {
  description = "Whether to enable detailed monitoring"
  type        = bool
}

variable "associate_public_ip_address" {
  description = "Whether to associate a public IP"
  type        = bool
}

variable "additional_tags" {
  description = "Additional tags for this environment"
  type        = map(string)
}