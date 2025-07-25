provider "aws" {
  region = var.aws_region
}

# Criar o repositório ECR
resource "aws_ecr_repository" "product_catalog_repository" {
  name = var.repository_name

  image_scanning_configuration {
    scan_on_push = true
  }

  image_tag_mutability = "MUTABLE"
}

# Criar o ECS Cluster
resource "aws_ecs_cluster" "product_catalog_cluster" {
  name = var.cluster_name
}

# Usar o security group padrão da VPC
data "aws_security_group" "default" {
  name   = "default"
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Definir a Task Definition do ECS (usando a imagem do repositório ECR)
resource "aws_ecs_task_definition" "product_catalog_task" {
  family                   = "product-catalog-task"
  container_definitions    = jsonencode([{
    name      = "product-catalog-container"
    image     = aws_ecr_repository.product_catalog_repository.repository_url
    cpu       = 256
    memory    = 512
    essential = true
    portMappings = [
      {
        containerPort = 80
        hostPort      = 80
        protocol      = "tcp"
      }
    ]
  }])

  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
}

# Criar o ECS Service (onde o container será executado)
resource "aws_ecs_service" "product_catalog_service" {
  name            = "product-catalog-service"
  cluster         = aws_ecs_cluster.product_catalog_cluster.id
  task_definition = aws_ecs_task_definition.product_catalog_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups = [data.aws_security_group.default.id]
    subnets          = data.aws_subnets.default.ids
    assign_public_ip = true
  }
}
