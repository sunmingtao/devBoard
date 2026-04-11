environment                   = "prod"
aws_region                    = "ap-southeast-2"
instance_name                 = "devboard-prod"
instance_type                 = "t3.small"
frontend_port                 = 80
ssh_allowed_cidr              = "119.18.2.3/32"
root_volume_size              = 30
enable_termination_protection = true
monitoring_enabled            = true
associate_public_ip_address   = true

additional_tags = {
  Owner      = "Mingtao"
  CostCenter = "production"
}