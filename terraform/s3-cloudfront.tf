# S3 and CloudFront for Development Frontend

# S3 Bucket for Frontend
resource "aws_s3_bucket" "dev_frontend" {
  bucket = "${var.project_name}-${var.environment}-frontend-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "${var.project_name}-${var.environment}-frontend"
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 Bucket Public Access Block (keeping it private)
resource "aws_s3_bucket_public_access_block" "dev_frontend" {
  bucket = aws_s3_bucket.dev_frontend.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Policy for CloudFront
resource "aws_s3_bucket_policy" "dev_frontend" {
  bucket = aws_s3_bucket.dev_frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontAccess"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.dev_frontend.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.dev_frontend.arn
          }
        }
      }
    ]
  })
}

# CloudFront Origin Access Control
resource "aws_cloudfront_origin_access_control" "dev_frontend" {
  name                              = "${var.project_name}-${var.environment}-frontend-oac"
  description                       = "OAC for ${var.project_name} ${var.environment} frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "dev_frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  price_class         = "PriceClass_100"  # Use only North America and Europe (cheaper for dev)

  # Origin 1: S3 bucket for static frontend files
  origin {
    domain_name              = aws_s3_bucket.dev_frontend.bucket_regional_domain_name
    origin_id                = aws_s3_bucket.dev_frontend.id
    origin_access_control_id = aws_cloudfront_origin_access_control.dev_frontend.id
  }

  # Origin 2: ALB for API proxy
  origin {
    domain_name = aws_lb.dev_alb.dns_name
    origin_id   = "dev-alb-api"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"  # ALB doesn't have HTTPS cert
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # Default behavior: serve frontend from S3
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = aws_s3_bucket.dev_frontend.id

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  # API behavior: proxy to ALB
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "dev-alb-api"

    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Content-Type", "Accept"]
      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }

  # Custom error page for SPA routing
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-frontend-cf"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Outputs
output "dev_frontend_bucket_name" {
  description = "Name of the dev frontend S3 bucket"
  value       = aws_s3_bucket.dev_frontend.id
}

output "dev_cloudfront_domain" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.dev_frontend.domain_name
}

output "dev_cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.dev_frontend.id
}