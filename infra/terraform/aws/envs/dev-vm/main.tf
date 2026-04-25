terraform {
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

module "network" {
  source = "../../modules/network"

  name_prefix = var.name_prefix
  environment = var.environment
  vpc_cidr    = var.vpc_cidr

  availability_zones = var.availability_zones

  public_subnet_cidrs = var.public_subnet_cidrs

  private_db_subnet_cidrs = var.private_db_subnet_cidrs

  additional_tags = var.additional_tags
}

module "single_vm" {
  source = "../../modules/single-vm"

  environment                   = var.environment
  instance_name                 = var.instance_name
  instance_type                 = var.instance_type
  ami_id                        = var.ami_id
  frontend_port                 = var.frontend_port
  ssh_allowed_cidr              = var.ssh_allowed_cidr
  public_key                    = var.public_key
  root_volume_size              = var.root_volume_size
  enable_termination_protection = var.enable_termination_protection
  monitoring_enabled            = var.monitoring_enabled
  associate_public_ip_address   = var.associate_public_ip_address
  additional_tags               = var.additional_tags

  vpc_id    = module.network.vpc_id
  subnet_id = module.network.public_subnet_ids[0]
}

resource "aws_route53_record" "app" {
  zone_id = var.route53_zone_id
  name    = var.domain_name
  type    = "A"
  ttl     = 300
  records = [module.single_vm.elastic_ip]
}

module "rds_mysql" {
  source = "../../modules/rds-mysql"

  environment                = var.environment
  vpc_id                     = module.network.vpc_id
  subnet_ids                 = module.network.private_db_subnet_ids
  allowed_security_group_ids = {
    app_vm = module.single_vm.vm_security_group_id
  }

  db_instance_identifier = var.db_instance_identifier
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password

  instance_class          = var.db_instance_class
  allocated_storage       = var.db_allocated_storage
  max_allocated_storage   = var.db_max_allocated_storage
  multi_az                = var.db_multi_az
  deletion_protection     = var.db_deletion_protection
  skip_final_snapshot     = var.db_skip_final_snapshot
  backup_retention_period = var.db_backup_retention_period

  additional_tags = var.additional_tags
}

module "scheduler" {
  source = "../../modules/scheduler"

  name_prefix = "devboard-dev"
  environment = var.environment

  tag_key   = "AutoSchedule"
  tag_value = "true"

  start_schedule_expression = "cron(0 21 * * ? *)"
  stop_schedule_expression  = "cron(0 13 * * ? *)"

  additional_tags = var.additional_tags
}