data "archive_file" "start_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_start.py"
  output_path = "${path.module}/lambda_start.zip"
}

data "archive_file" "stop_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_stop.py"
  output_path = "${path.module}/lambda_stop.zip"
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.name_prefix}-scheduler-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "scheduler_ec2_policy" {
  name        = "${var.name_prefix}-scheduler-ec2-policy"
  description = "Allow Lambda to describe, start, and stop EC2 instances"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DescribeInstances"
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances"
        ]
        Resource = "*"
      },
      {
        Sid    = "StartStopInstances"
        Effect = "Allow"
        Action = [
          "ec2:StartInstances",
          "ec2:StopInstances"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "scheduler_ec2_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.scheduler_ec2_policy.arn
}

resource "aws_lambda_function" "start_ec2" {
  function_name = "${var.name_prefix}-start-ec2"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_start.lambda_handler"
  runtime       = "python3.12"
  filename      = data.archive_file.start_lambda_zip.output_path
  source_code_hash = data.archive_file.start_lambda_zip.output_base64sha256
  timeout       = 30

  environment {
    variables = {
      TAG_KEY   = var.tag_key
      TAG_VALUE = var.tag_value
    }
  }

  tags = local.common_tags
}

resource "aws_lambda_function" "stop_ec2" {
  function_name = "${var.name_prefix}-stop-ec2"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_stop.lambda_handler"
  runtime       = "python3.12"
  filename      = data.archive_file.stop_lambda_zip.output_path
  source_code_hash = data.archive_file.stop_lambda_zip.output_base64sha256
  timeout       = 30

  environment {
    variables = {
      TAG_KEY   = var.tag_key
      TAG_VALUE = var.tag_value
    }
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_event_rule" "start_rule" {
  name                = "${var.name_prefix}-start-ec2-rule"
  description         = "Start tagged EC2 instances on schedule"
  schedule_expression = var.start_schedule_expression

  tags = local.common_tags
}

resource "aws_cloudwatch_event_rule" "stop_rule" {
  name                = "${var.name_prefix}-stop-ec2-rule"
  description         = "Stop tagged EC2 instances on schedule"
  schedule_expression = var.stop_schedule_expression

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "start_target" {
  rule      = aws_cloudwatch_event_rule.start_rule.name
  target_id = "StartEC2LambdaTarget"
  arn       = aws_lambda_function.start_ec2.arn
}

resource "aws_cloudwatch_event_target" "stop_target" {
  rule      = aws_cloudwatch_event_rule.stop_rule.name
  target_id = "StopEC2LambdaTarget"
  arn       = aws_lambda_function.stop_ec2.arn
}

resource "aws_lambda_permission" "allow_eventbridge_start" {
  statement_id  = "AllowExecutionFromEventBridgeStart"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start_ec2.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.start_rule.arn
}

resource "aws_lambda_permission" "allow_eventbridge_stop" {
  statement_id  = "AllowExecutionFromEventBridgeStop"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stop_ec2.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.stop_rule.arn
}

locals {
  common_tags = merge(
    {
      Project     = "DevBoard"
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}