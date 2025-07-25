# Buscar a VPC padrão
data "aws_vpc" "default" {
  filter {
    name   = "isDefault"
    values = ["true"]
  }
}

# Buscar as subnets da VPC padrão
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Buscar o security group padrão da VPC
data "aws_security_group" "default" {
  name   = "default"
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}
