resource "aws_sns_topic" "alerts" {
  name = "devboard-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "sunmingtao@gmail.com"
}

resource "aws_route53_health_check" "app_health" {
  fqdn          = var.domain_name
  port          = 443
  type          = "HTTPS"
  resource_path = "/api/health"

  request_interval  = 30
  failure_threshold = 3

  tags = {
    Name = "devboard-health-check"
  }
}

resource "aws_cloudwatch_metric_alarm" "health_check_alarm" {
  alarm_name          = "devboard-health-check-failed"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  threshold           = 1

  metric_name = "HealthCheckStatus"
  namespace   = "AWS/Route53"
  period      = 60
  statistic   = "Minimum"

  dimensions = {
    HealthCheckId = aws_route53_health_check.app_health.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]

  treat_missing_data = "breaching"
}

resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  alarm_name          = "devboard-ec2-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 70

  metric_name = "CPUUtilization"
  namespace   = "AWS/EC2"
  period      = 300
  statistic   = "Average"

  dimensions = {
    InstanceId = module.single_vm.instance_id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}