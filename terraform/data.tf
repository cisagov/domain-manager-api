# ===================================
# Hosted Zone Credentials
# ===================================
data "aws_ssm_parameter" "hosted_zone_id" {
  name = "/${var.env}/${var.app}/hosted-zone-id"
}
