variable "name_prefix" {
  description = "Prefix for scheduler resource names"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "tag_key" {
  description = "Tag key used to select EC2 instances"
  type        = string
  default     = "AutoSchedule"
}

variable "tag_value" {
  description = "Tag value used to select EC2 instances"
  type        = string
  default     = "true"
}

variable "start_schedule_expression" {
  description = "EventBridge schedule expression for starting EC2"
  type        = string
}

variable "stop_schedule_expression" {
  description = "EventBridge schedule expression for stopping EC2"
  type        = string
}

variable "additional_tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}