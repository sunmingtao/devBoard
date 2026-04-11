terraform {
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

module "single_vm" {
  source = "../../modules/single-vm"

  environment                   = var.environment
  instance_name                 = var.instance_name
  instance_type                 = var.instance_type
  app_port                      = var.app_port
  ssh_allowed_cidr              = var.ssh_allowed_cidr
  public_key                    = var.public_key
  root_volume_size              = var.root_volume_size
  enable_termination_protection = var.enable_termination_protection
  monitoring_enabled            = var.monitoring_enabled
  associate_public_ip_address   = var.associate_public_ip_address
  additional_tags               = var.additional_tags
}