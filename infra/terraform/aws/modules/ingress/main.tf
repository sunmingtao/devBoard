resource "kubernetes_ingress_v1" "this" {
  metadata {
    name      = var.name
    namespace = var.namespace

    annotations = {
      "kubernetes.io/ingress.class"                    = "alb"
      "alb.ingress.kubernetes.io/scheme"               = "internet-facing"
      "alb.ingress.kubernetes.io/target-type"          = "ip"
      "alb.ingress.kubernetes.io/listen-ports"         = "[{\"HTTP\":80},{\"HTTPS\":443}]"
      "alb.ingress.kubernetes.io/certificate-arn"      = var.certificate_arn
      "alb.ingress.kubernetes.io/ssl-redirect"         = "443"
      "alb.ingress.kubernetes.io/healthcheck-path"     = "/api/health"
      "alb.ingress.kubernetes.io/success-codes"        = "200"
    }
  }

  spec {
    rule {
      host = var.host

      http {
        path {
          path      = "/api"
          path_type = "Prefix"

          backend {
            service {
              name = var.backend_service_name
              port {
                number = var.backend_service_port
              }
            }
          }
        }

        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = var.frontend_service_name
              port {
                number = var.frontend_service_port
              }
            }
          }
        }
      }
    }
  }
}