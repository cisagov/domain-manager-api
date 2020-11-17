# ===================================
# Route 53
# ===================================
resource "aws_route53_record" "domain" {
  zone_id = data.aws_route53_zone.zone.zone_id
  name    = "${var.app}.${var.env}.${data.aws_route53_zone.zone.name}"
  type    = "CNAME"
  ttl     = "300"
  records = [module.alb.alb_dns_name]
}

# ===========================
# Certs
# ===========================
resource "aws_acm_certificate" "cert" {
  domain_name       = aws_route53_record.domain.name
  validation_method = "DNS"

  tags = {
    Environment = var.env
  }

  lifecycle {
    create_before_destroy = true
  }
}

# resource "aws_route53_record" "validation" {
#   allow_overwrite = true
#   name            = aws_acm_certificate.cert.domain_validation_options[0].resource_record_name
#   records         = [aws_acm_certificate.cert.domain_validation_options[0].resource_record_value]
#   ttl             = 60
#   type            = aws_acm_certificate.cert.domain_validation_options[0].resource_record_type
#   zone_id         = data.aws_route53_zone.zone.zone_id
# }

# resource "aws_acm_certificate_validation" "validation" {
#   certificate_arn         = aws_acm_certificate.cert.arn
#   validation_record_fqdns = [aws_route53_record.validation.fqdn]
# }


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
