variable "environment" {
  description = "Environment name (dev or prod)"
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

variable "public_key" {
  description = "SSH public key Content"
  type        = string
}

variable "root_volume_size" {
  description = "Root EBS size"
  type        = number
  default     = 20
}

variable "enable_termination_protection" {
  description = "Whether to enable EC2 termination protection"
  type        = bool
  default     = false
}

variable "monitoring_enabled" {
  description = "Whether to enable detailed monitoring"
  type        = bool
  default     = false
}

variable "associate_public_ip_address" {
  description = "Whether to associate a public IP address"
  type        = bool
  default     = true
}

variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}