resource "aws_secretsmanager_secret" "devboard_backend" {
  name                    = var.backend_secret_name
  description             = "DevBoard backend runtime secrets for EKS"
  recovery_window_in_days = 7

  tags = merge(
    local.common_tags,
    {
      Name = var.backend_secret_name
    }
  )
}

resource "aws_secretsmanager_secret_version" "devboard_backend" {
  secret_id = aws_secretsmanager_secret.devboard_backend.id

  secret_string = jsonencode({
    DATABASE_PASSWORD = var.db_password
    JWT_SECRET        = var.jwt_secret
  })
}

resource "aws_iam_role" "external_secrets" {
  name = "${local.cluster_name}-external-secrets"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = module.eks.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(module.eks.oidc_provider_url, "https://", "")}:aud" = "sts.amazonaws.com"
            "${replace(module.eks.oidc_provider_url, "https://", "")}:sub" = "system:serviceaccount:external-secrets:external-secrets"
          }
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_policy" "external_secrets" {
  name = "${local.cluster_name}-external-secrets-secretsmanager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretValue",
          "secretsmanager:ListSecretVersionIds"
        ]
        Resource = aws_secretsmanager_secret.devboard_backend.arn
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "external_secrets" {
  role       = aws_iam_role.external_secrets.name
  policy_arn = aws_iam_policy.external_secrets.arn
}
