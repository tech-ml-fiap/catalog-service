provider "aws" {
  region = var.aws_region
}

# Obter a identidade da conta AWS (para usar o ARN da role LabRole)
data "aws_caller_identity" "current" {}

# Criar o ECS Cluster
resource "aws_ecs_cluster" "product_catalog_cluster" {
  name = var.cluster_name
}

# Usar o repositório ECR existente
data "aws_ecr_repository" "product_catalog_repository" {
  name = var.repository_name
}

# Usar a role existente 'LabRole' para a execução do ECS Fargate
resource "aws_ecs_task_definition" "product_catalog_task" {
  family                   = "product-catalog-task"
  container_definitions    = jsonencode([{
    name      = "product-catalog-container"
    image     = data.aws_ecr_repository.product_catalog_repository.repository_url
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
  execution_role_arn       = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"  # Usando a role 'LabRole'
}

data "aws_ecs_service" "existing_service" {
  cluster_arn = aws_ecs_cluster.product_catalog_cluster.arn
  service_name = "product-catalog-service"
}

resource "aws_ecs_service" "product_catalog_service" {
  count           = length(data.aws_ecs_service.existing_service) == 0 ? 1 : 0
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

  lifecycle {
    ignore_changes = [
      task_definition,
      desired_count
    ]
  }
}
