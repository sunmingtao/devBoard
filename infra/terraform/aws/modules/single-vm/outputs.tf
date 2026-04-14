output "instance_id" {
  value = aws_instance.vm.id
}

output "public_ip" {
  value = aws_instance.vm.public_ip
}

output "public_dns" {
  value = aws_instance.vm.public_dns
}

output "vm_security_group_id" {
  value = aws_security_group.vm_sg.id
}

output "subnet_id" {
  value = aws_instance.vm.subnet_id
}