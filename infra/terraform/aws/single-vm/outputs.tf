output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.devboard.id
}

output "public_ip" {
  description = "EC2 public IP"
  value       = aws_instance.devboard.public_ip
}

output "public_dns" {
  description = "EC2 public DNS"
  value       = aws_instance.devboard.public_dns
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ${var.private_key_path} ec2-user@${aws_instance.devboard.public_ip}"
}