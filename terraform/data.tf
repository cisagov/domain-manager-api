# Route 53 Zone
data "aws_route53_zone" "zone" {
  name = var.route53_zone_name
}
