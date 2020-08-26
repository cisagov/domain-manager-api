# ===================================
# Hosted Zone Credentials
# ===================================
data "aws_ssm_parameter" "hosted_zone_id" {
  name = "/${var.env}/${var.app}/hosted-zone-id"
}


# Route 53 Zone
data "aws_route53_zone" "zone" {
  name = var.route53_zone_name
}
