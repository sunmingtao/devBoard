terraform {
  required_version = ">= 1.5.0"

  required_providers {
    vultr = {
      source  = "vultr/vultr"
      version = "~> 2.26"
    }
  }
}

provider "vultr" {
  api_key = var.vultr_api_key
}

variable "vultr_api_key" {
  type      = string
  sensitive = true
}

variable "region" {
  type    = string
  default = "syd"
}

variable "plan" {
  type    = string
  default = "vc2-8c-32gb"
}

variable "label" {
  type    = string
  default = "devboard-vm"
}

variable "os_id" {
  type    = number
  default = 1743
}

resource "vultr_instance" "devboard" {
  region = var.region
  plan   = var.plan
  label  = var.label
  os_id  = var.os_id

  hostname = "devboard-vm"
  user_data = <<-EOF
#cloud-config
package_update: true
package_upgrade: false

packages:
  - ca-certificates
  - curl
  - gnupg
  - git

ssh_authorized_keys:
  - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEoW5PjWl/E+UpF5phKPafcCQe7fm+EuU5KrOZ/iOgGS devboard
  - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOToPtAfRKiUHT0glR6VxCdytipJfL1oIdcz52C+Q+n2 jenkins-deploy

runcmd:
  - install -m 0755 -d /etc/apt/keyrings
  - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  - chmod a+r /etc/apt/keyrings/docker.gpg
  - echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list
  - apt-get update
  - apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  - systemctl enable docker
  - systemctl start docker
  - mkdir -p /opt/devboard
EOF
}

output "instance_ip" {
  value = vultr_instance.devboard.main_ip
}
