environment = "dev"
aws_region  = "ap-southeast-2"
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
instance_type                 = "t3.micro"
frontend_port                 = 80
ssh_allowed_cidr              = "119.18.2.3/32"
root_volume_size              = 30
enable_termination_protection = false
monitoring_enabled            = false
associate_public_ip_address   = true

db_instance_identifier = "devboard-dev-db"
db_name                = "devboard"
db_username            = "devboard_user"
db_password            = "devboard_password"

db_instance_class          = "db.t3.micro"
db_allocated_storage       = 20
db_max_allocated_storage   = 100
db_multi_az                = false
db_deletion_protection     = false
db_skip_final_snapshot     = true
db_backup_retention_period = 7

additional_tags = {
  Owner      = "Mingtao"
  CostCenter = "learning"
}

domain_name     = "smtdevboard.com"
route53_zone_id = "Z02400223BOTRAEUO0YCG"