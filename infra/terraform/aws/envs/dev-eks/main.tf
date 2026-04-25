terraform {
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

locals {
  cluster_name            = "${var.name_prefix}-eks"
  multi_az                = false
  deletion_protection     = false
  skip_final_snapshot     = true
  backup_retention_period = 1
  max_allocated_storage   = 100
}

data "terraform_remote_state" "dev_vm" {
  backend = "s3"

  config = {
    bucket = "devboard-terraform-state"
    key    = "env/dev/single-vm/terraform.tfstate"
    region = "ap-southeast-2"
  }
}

module "rds_mysql" {
  source = "../../modules/rds-mysql"

  environment = var.environment
  vpc_id      = data.terraform_remote_state.dev_vm.outputs.vpc_id
  subnet_ids  = data.terraform_remote_state.dev_vm.outputs.private_db_subnet_ids

  allowed_security_group_ids = {
    eks_cluster = module.eks.cluster_security_group_id
  }

  db_instance_identifier = var.db_instance_identifier
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password

  instance_class          = var.db_instance_class
  allocated_storage       = var.db_allocated_storage
  max_allocated_storage   = local.max_allocated_storage
  multi_az                = local.multi_az
  deletion_protection     = local.deletion_protection
  skip_final_snapshot     = local.skip_final_snapshot
  backup_retention_period = local.backup_retention_period

  additional_tags = var.additional_tags
}

module "eks" {
  source = "../../modules/eks"

  cluster_name    = local.cluster_name
  cluster_version = "1.31"
  environment     = var.environment

  vpc_id     = data.terraform_remote_state.dev_vm.outputs.vpc_id
  subnet_ids = data.terraform_remote_state.dev_vm.outputs.public_subnet_ids

  node_group_name = "devboard-ng"
  desired_size    = 2
  min_size        = 1
  max_size        = 2
  instance_types  = ["t3.small"]

  additional_tags = var.additional_tags
}

module "alb_controller" {
  source = "../../modules/alb-controller"

  cluster_name                       = module.eks.cluster_name
  cluster_endpoint                   = module.eks.cluster_endpoint
  cluster_certificate_authority_data = module.eks.cluster_certificate_authority_data
  oidc_provider_arn                  = module.eks.oidc_provider_arn
  oidc_provider_url                  = module.eks.oidc_provider_url
  region                             = var.aws_region
  vpc_id                             = data.terraform_remote_state.dev_vm.outputs.vpc_id
}

data "aws_acm_certificate" "www" {
  domain      = "smtdevboard.com"
  statuses    = ["ISSUED"]
  most_recent = true
}

module "ingress" {
  source = "../../modules/ingress"

  namespace = "devboard"
  name      = "devboard-ingress"
  host      = "www.smtdevboard.com"

  certificate_arn = data.aws_acm_certificate.www.arn

  frontend_service_name = "devboard-frontend"
  frontend_service_port = 80

  backend_service_name = "devboard-backend"
  backend_service_port = 8080

  cluster_endpoint                   = module.eks.cluster_endpoint
  cluster_certificate_authority_data = module.eks.cluster_certificate_authority_data
}

data "aws_elb_hosted_zone_id" "this" {

}

resource "aws_route53_record" "www" {
  zone_id = var.route53_zone_id
  name    = "www.smtdevboard.com"
  type    = "A"

  allow_overwrite = true

  alias {
    name                   = module.ingress.ingress_hostname
    zone_id                = data.aws_elb_hosted_zone_id.this.id
    evaluate_target_health = true
  }
}
