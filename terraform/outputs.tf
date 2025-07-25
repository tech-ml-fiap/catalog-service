output "ecr_repository_url" {
  description = "The ECR repository URL for storing Docker images"
  value       = aws_ecr_repository.product_catalog_repository.repository_url
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.product_catalog_cluster.name
}

output "ecs_service_name" {
  description = "The name of the ECS service"
  value       = aws_ecs_service.product_catalog_service.name
}

output "ecs_service_url" {
  description = "The public URL of the ECS service"
  value       = "http://${aws_ecs_service.product_catalog_service.load_balancer[0].dns_name}"
}
