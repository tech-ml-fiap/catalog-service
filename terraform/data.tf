# Obter a VPC padrão
data "aws_vpc" "default" {
  filter {
    name   = "isDefault"
    values = ["true"]
  }
}

# Obter as subnets da VPC padrão
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Obter o security group padrão da VPC
data "aws_security_group" "default" {
  name   = "default"
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}
