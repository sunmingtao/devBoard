terraform {
  backend "s3" {
    bucket         = "devboard-terraform-state"
    key            = "single-vm/terraform.tfstate"
    region         = "ap-southeast-2"
    dynamodb_table = "terraform-lock"
  }
}