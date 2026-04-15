output "start_lambda_function_name" {
  value = aws_lambda_function.start_ec2.function_name
}

output "stop_lambda_function_name" {
  value = aws_lambda_function.stop_ec2.function_name
}

output "start_rule_name" {
  value = aws_cloudwatch_event_rule.start_rule.name
}

output "stop_rule_name" {
  value = aws_cloudwatch_event_rule.stop_rule.name
}