# ===================================
# Document DB
# ===================================
resource "random_string" "docdb_username" {
  length  = 8
  number  = false
  special = false
  upper   = false
}

resource "aws_ssm_parameter" "docdb_username" {
  name        = "/${var.env}/${var.app}/docdb/username/master"
  description = "The username for document db"
  type        = "SecureString"
  value       = random_string.docdb_username.result
}

resource "random_password" "docdb_password" {
  length           = 32
  special          = true
  override_special = "!_#&"
}

resource "aws_ssm_parameter" "docdb_password" {
  name        = "/${var.env}/${var.app}/docdb/password/master"
  description = "The password for document db"
  type        = "SecureString"
  value       = random_password.docdb_password.result
}

module "documentdb" {
  source                  = "github.com/cloudposse/terraform-aws-documentdb-cluster"
  stage                   = "${var.env}"
  name                    = "${var.env}-${var.app}-docdb"
  cluster_size            = 1
  master_username         = random_string.docdb_username.result
  master_password         = random_password.docdb_password.result
  instance_class          = var.docdb_instance_class
  vpc_id                  = var.vpc_id
  subnet_ids              = var.public_subnet_ids
  allowed_cidr_blocks     = ["0.0.0.0/0"]
  allowed_security_groups = [aws_security_group.api.id]
  skip_final_snapshot     = true
}

# ===================================
# S3
# ===================================
resource "aws_s3_bucket" "websites" {
  bucket = "${var.app}-${var.env}-websites"
  acl    = "public-read"
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Public",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${var.app}-${var.env}-websites/*"
    }
  ]
}
POLICY

  website {
    index_document = "index.html"
  }
}

resource "aws_s3_bucket" "templates" {
  bucket = "${var.app}-${var.env}-templates"
  acl    = "private"
}

# ===================================
# Credentials
# ===================================
resource "random_password" "api_key" {
  length  = 32
  number  = false
  special = false
  upper   = true
}

resource "aws_ssm_parameter" "api_key" {
  name        = "/${var.env}/${var.app}/api/key"
  description = "api key for ${var.app}"
  type        = "SecureString"
  value       = random_password.api_key.result
}

# ===================================
# Container Definition
# ===================================
locals {
  api_port    = 5000
  api_lb_port = 8043

  environment = {
    "FLASK_APP" : "main",
    "FLASK_ENV" : "development",
    "DEBUG" : 1,
    "DB_HOST" : module.documentdb.endpoint,
    "DB_PORT" : 27017,
    "MONGO_TYPE" : "DOCUMENTDB",
    "WEBSITE_STORAGE" : aws_s3_bucket.websites.id,
    "WEBSITE_STORAGE_URL" : aws_s3_bucket.websites.website_endpoint,
    "SOURCE_BUCKET" : aws_s3_bucket.websites.id,
    "NC_IP" : "0.0.0.0",
    "BROWSERLESS_ENDPOINT" : module.browserless.lb_dns_name,
    "WORKERS" : 4
  }

  secrets = {
    "API_KEY" : aws_ssm_parameter.api_key.arn,
    "DB_PW" : aws_ssm_parameter.docdb_password.arn,
    "DB_USER" : aws_ssm_parameter.docdb_username.arn,
    "HOSTED_ZONE_ID" : data.aws_ssm_parameter.hosted_zone_id.arn,
  }
}

module "api_container" {
  source    = "github.com/cisagov/fargate-container-def-tf-module"
  namespace = var.app
  stage     = var.env
  name      = "api"

  container_name  = "${var.app}-api"
  container_image = "${var.image_repo}:${var.image_tag}"
  container_port  = local.api_port
  region          = var.region
  log_retention   = 7
  environment     = local.environment
  secrets         = local.secrets
}

# ===================================
# Fargate Service
# ===================================
data "aws_iam_policy_document" "api" {
  statement {
    actions = [
      "s3:*",
      "route53:*"
    ]

    resources = [
      "*"
    ]
  }
}

module "api_fargate" {
  source    = "github.com/cisagov/fargate-service-tf-module"
  namespace = var.app
  stage     = var.env
  name      = "api"

  https_cert_arn        = aws_acm_certificate.cert.arn
  container_port        = local.api_port
  container_definition  = module.api_container.json
  container_name        = "${var.app}-api"
  cpu                   = 2048
  memory                = 4096
  vpc_id                = var.vpc_id
  health_check_interval = 60
  health_check_path     = "/"
  health_check_codes    = "200"
  iam_policy_document   = data.aws_iam_policy_document.api.json
  load_balancer_arn     = module.alb.alb_arn
  load_balancer_port    = local.api_lb_port
  desired_count         = 1
  subnet_ids            = var.private_subnet_ids
  security_group_ids    = [aws_security_group.api.id]
}

# ===================================
# Security Groups
# ===================================
resource "aws_security_group" "api" {
  name        = "${var.app}-${var.env}-api-alb"
  description = "Allow traffic for api from alb"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow container port from ALB"
    from_port       = local.api_port
    to_port         = local.api_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    self            = true
  }

  egress {
    description = "Allow outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    "Name" = "${var.app}-${var.env}-api-alb"
  }
}

# ===========================
# BROWSERLESS
# ===========================
module "browserless" {
  source    = "github.com/cisagov/fargate-browserless-tf-module"
  region    = var.region
  namespace = var.app
  stage     = var.env
  name      = "browserless"

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnet_ids
  lb_port    = 3000
}
