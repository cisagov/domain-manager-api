# ===================================
# Certs
# ===================================
resource "tls_private_key" "_" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "_" {
  key_algorithm         = tls_private_key._.algorithm
  private_key_pem       = tls_private_key._.private_key_pem
  validity_period_hours = 720
  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth"
  ]

  dns_names = [module.alb.alb_dns_name]

  subject {
    common_name  = module.alb.alb_dns_name
    organization = "${var.app}-${var.env}-alb"
  }
}

resource "aws_iam_server_certificate" "_" {
  name             = "${var.app}-${var.env}-alb"
  certificate_body = tls_self_signed_cert._.cert_pem
  private_key      = tls_private_key._.private_key_pem
}


# ===================================
# Load Balancer
# ===================================
resource "aws_security_group" "alb" {
  name        = "${var.app}-${var.env}-alb"
  description = "Allowed ports into alb"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    "Name" = "${var.app}-${var.env}-alb"
  }
}

module "alb" {
  source             = "github.com/cloudposse/terraform-aws-alb"
  namespace          = var.app
  stage              = var.env
  name               = "public-alb"
  http_enabled       = false
  internal           = false
  vpc_id             = var.vpc_id
  security_group_ids = [aws_security_group.alb.id]
  subnet_ids         = var.public_subnet_ids
  target_group_name  = "${var.app}-${var.env}-tg"
}

#=================================================
#  COGNITO
#=================================================
resource "aws_cognito_user_pool" "pool" {
  name = "${var.app}-${var.env}-users"
}

resource "aws_cognito_user_pool_client" "client" {
  name                                 = "${var.app}-${var.env}-client"
  user_pool_id                         = aws_cognito_user_pool.pool.id
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["aws.cognito.signin.user.admin", "email", "openid", "phone", "profile"]
  callback_urls                        = ["https://${module.alb.alb_dns_name}"]
  explicit_auth_flows                  = ["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_CUSTOM_AUTH", "ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_PASSWORD_AUTH", "ALLOW_USER_SRP_AUTH"]
  logout_urls                          = ["https://${module.alb.alb_dns_name}"]
  supported_identity_providers         = ["COGNITO"]
}

resource "aws_cognito_user_pool_domain" "domain" {
  domain       = "${var.app}-${var.env}"
  user_pool_id = aws_cognito_user_pool.pool.id
}

resource "aws_ssm_parameter" "client_id" {
  name        = "/${var.env}/${var.app}/cognito/client/id"
  description = "The client id for the client"
  type        = "SecureString"
  value       = aws_cognito_user_pool_client.client.id
}

resource "aws_ssm_parameter" "domain" {
  name        = "/${var.env}/${var.app}/cognito/domain"
  description = "The domain for user pool"
  type        = "SecureString"
  value       = aws_cognito_user_pool_domain.domain.domain
}
