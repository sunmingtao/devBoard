output "instance_id" {
  value = module.single_vm.instance_id
}

output "public_ip" {
  value = module.single_vm.public_ip
}

output "public_dns" {
  value = module.single_vm.public_dns
}

output "vm_security_group_id" {
  value = module.single_vm.vm_security_group_id
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "public_subnet_ids" {
  value = module.network.public_subnet_ids
}

output "private_db_subnet_ids" {
  value = module.network.private_db_subnet_ids
}