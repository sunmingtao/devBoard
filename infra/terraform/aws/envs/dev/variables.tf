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

variable "frontend_port" {
  description = "Application port"
  type        = number
}

variable "ssh_allowed_cidr" {
  description = "Allowed CIDR for SSH"
  type        = string
}

variable "public_key" {
  description = "SSH public key content"
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

variable "name_prefix" {
  description = "Prefix for naming network resources"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
}

variable "public_subnet_cidrs" {
  description = "CIDRs for public subnets"
  type        = list(string)
}

variable "private_db_subnet_cidrs" {
  description = "CIDRs for private DB subnets"
  type        = list(string)
}

variable "db_instance_identifier" {
  description = "RDS instance identifier"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "db_username" {
  description = "Database master username"
  type        = string
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Max allocated storage for RDS autoscaling"
  type        = number
  default     = 100
}

variable "db_multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
  default     = false
}

variable "db_deletion_protection" {
  description = "Enable deletion protection for RDS"
  type        = bool
  default     = false
}

variable "db_skip_final_snapshot" {
  description = "Skip final snapshot on deletion"
  type        = bool
  default     = true
}

variable "db_backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}