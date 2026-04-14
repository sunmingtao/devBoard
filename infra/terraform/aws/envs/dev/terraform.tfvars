environment                   = "dev"
aws_region                    = "ap-southeast-2"
name_prefix = "devboard-dev"
vpc_cidr    = "10.0.0.0/16"

availability_zones = [
  "ap-southeast-2a",
  "ap-southeast-2b"
]

public_subnet_cidrs = [
  "10.0.1.0/24",
  "10.0.2.0/24"
]

private_db_subnet_cidrs = [
  "10.0.11.0/24",
  "10.0.12.0/24"
]
instance_name                 = "devboard-dev-vm"
instance_type                 = "t3.small"
frontend_port                 = 80
ssh_allowed_cidr              = "119.18.2.3/32"
root_volume_size              = 30
enable_termination_protection = false
monitoring_enabled            = false
associate_public_ip_address   = true

additional_tags = {
  Owner      = "Mingtao"
  CostCenter = "learning"
}