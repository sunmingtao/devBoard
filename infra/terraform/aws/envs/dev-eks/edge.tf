provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  config_path            = "~/.kube/config"
}

data "aws_acm_certificate" "www" {
  domain      = "smtdevboard.com"
  statuses    = ["ISSUED"]
  most_recent = true
}

module "ingress" {
  count  = var.enable_ingress ? 1 : 0
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

data "aws_elb_hosted_zone_id" "this" {}

resource "aws_route53_record" "www" {
  count = var.enable_route53 ? 1 : 0

  zone_id = var.route53_zone_id
  name    = "www.smtdevboard.com"
  type    = "A"

  allow_overwrite = true

  alias {
    name                   = module.ingress[0].ingress_hostname
    zone_id                = data.aws_elb_hosted_zone_id.this.id
    evaluate_target_health = true
  }
}