output "db_address" {
  value = module.rds_mysql.db_address
}

output "db_endpoint" {
  value = module.rds_mysql.db_endpoint
}

output "backend_secret_name" {
  value = aws_secretsmanager_secret.devboard_backend.name
}

output "external_secrets_role_arn" {
  value = aws_iam_role.external_secrets.arn
}
