bucket         = "devboard-terraform-state"
key            = "env/dev/single-vm/terraform.tfstate"
region         = "ap-southeast-2"
dynamodb_table = "terraform-lock"
encrypt        = true