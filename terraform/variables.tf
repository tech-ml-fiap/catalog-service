variable "aws_region" {
  default = "us-east-1"
}

variable "ecr_repo_name" {
  default = "product-catalog-repo"
}

variable "ecs_cluster_name" {
  default = "product-catalog-cluster"
}

variable "ecr_url" {
  description = "ECR URL for the product catalog container"
}
