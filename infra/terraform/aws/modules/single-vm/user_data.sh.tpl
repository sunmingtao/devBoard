#!/bin/bash
yum update -y

# install docker
yum install -y docker
systemctl start docker
systemctl enable docker

# allow ec2-user to run docker
usermod -aG docker ec2-user

# install docker-compose (simple version)
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

echo "VM ready. App should run on port ${app_port}"