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