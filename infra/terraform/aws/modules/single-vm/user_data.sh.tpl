#!/bin/bash
yum update -y

# install docker
yum install -y docker
systemctl start docker
systemctl enable docker

# allow ec2-user to run docker
usermod -aG docker ec2-user

# Install Docker Compose v2 plugin
mkdir -p /usr/libexec/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/libexec/docker/cli-plugins/docker-compose
chmod +x /usr/libexec/docker/cli-plugins/docker-compose

mkdir -p /opt/devboard
chown -R ec2-user:ec2-user /opt/devboard

echo "VM ready. App should run on port ${frontend_port}"