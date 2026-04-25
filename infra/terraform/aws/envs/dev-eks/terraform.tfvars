aws_region  = "ap-southeast-2"
name_prefix = "devboard-dev"
environment = "dev"

db_instance_identifier = "devboard-dev-eks-db"
db_name                = "devboard"
db_username            = "devboard_user"
db_password            = "devboard_password"

db_instance_class = "db.t3.micro"

additional_tags = {
  Owner      = "Mingtao"
  CostCenter = "learning"
}

route53_zone_id = "Z02400223BOTRAEUO0YCG"