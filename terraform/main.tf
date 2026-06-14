terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "app" {
  name        = "${var.project_name}-app-sg"
  description = "BiteScore application security group"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app" {
  ami                    = "ami-0a6282e52ede987c9" # Amazon Linux 2023 eu-central-1 — verify for your region
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.app.id]
  subnet_id              = data.aws_subnets.default.ids[0]

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker git
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ec2-user
    # Install docker-compose plugin and clone repo — customize for your deployment
    echo "BiteScore EC2 ready. Deploy via docker compose or manual setup."
  EOF

  tags = {
    Name    = "${var.project_name}-app"
    Project = var.project_name
  }
}

# Optional RDS — uncomment for production database
# resource "aws_db_instance" "postgres" {
#   identifier             = "${var.project_name}-db"
#   engine                 = "postgres"
#   engine_version         = "16"
#   instance_class         = "db.t3.micro"
#   allocated_storage      = 20
#   db_name                = "bitescore"
#   username               = "bitescore"
#   password               = var.db_password
#   vpc_security_group_ids = [aws_security_group.app.id]
#   skip_final_snapshot    = true
#   publicly_accessible    = false
# }
