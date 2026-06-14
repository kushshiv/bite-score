output "ec2_public_ip" {
  description = "Public IP of the BiteScore EC2 instance"
  value       = aws_instance.app.public_ip
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app.id
}

# output "rds_endpoint" {
#   description = "RDS PostgreSQL endpoint"
#   value       = aws_db_instance.postgres.endpoint
# }
