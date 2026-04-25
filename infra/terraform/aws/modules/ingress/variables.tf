variable "namespace" {
  type = string
}

variable "name" {
  type = string
}

variable "host" {
  type = string
}

variable "certificate_arn" {
  type = string
}

variable "frontend_service_name" {
  type = string
}

variable "frontend_service_port" {
  type = number
  default = 80
}

variable "backend_service_name" {
  type = string
}

variable "backend_service_port" {
  type = number
  default = 8080
}