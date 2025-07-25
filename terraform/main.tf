provider "aws" {
  region = var.aws_region
}

# Criando o repositório ECR para armazenar as imagens Docker
resource "aws_ecr_repository" "product_catalog_repository" {
  name = var.ecr_repo_name
}

# Criando um cluster ECS
resource "aws_ecs_cluster" "product_catalog_cluster" {
  name = var.ecs_cluster_name
}

# Security Group para o ECS
resource "aws_security_group" "ecs_security_group" {
  name_prefix = "ecs_sg_"
  description = "Allow inbound traffic to ECS containers"
  ingress {
    from_port   = 80
    to_port     = 80
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

# Definindo a Task no ECS Fargate
resource "aws_ecs_task_definition" "product_catalog_task" {
  family                   = "product-catalog-task"
  container_definitions    = jsonencode([{
    name      = "product-catalog-container"
    image     = var.ecr_url
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

# Criando o serviço ECS
resource "aws_ecs_service" "product_catalog_service" {
  name            = "product-catalog-service"
  cluster         = aws_ecs_cluster.product_catalog_cluster.id
  task_definition = aws_ecs_task_definition.product_catalog_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = [aws_subnet.main.id]
    security_groups = [aws_security_group.ecs_security_group.id]
    assign_public_ip = true
  }
}
