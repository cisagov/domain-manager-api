# ===================================
# NameCheap Credentials
# ===================================
data "aws_ssm_parameter" "nc_username" {
  name = "/${var.env}/${var.app}/namecheap/username"
}

data "aws_ssm_parameter" "nc_api_key" {
  name = "/${var.env}/${var.app}/namecheap/api-key"
}
