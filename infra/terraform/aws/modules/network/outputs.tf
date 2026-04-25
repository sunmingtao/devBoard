output "vpc_id" {
  value = aws_vpc.this.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_db_subnet_ids" {
  value = aws_subnet.private_db[*].id
}

output "public_subnet_cidrs" {
  value = aws_subnet.public[*].cidr_block
}

output "private_db_subnet_cidrs" {
  value = aws_subnet.private_db[*].cidr_block
}

output "internet_gateway_id" {
  value = aws_internet_gateway.this.id
}