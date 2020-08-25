terraform {
  backend "s3" {
    bucket         = "inl-tf-backend"
    key            = "domain-manager-api"
    region         = "us-east-1"
    dynamodb_table = "inl-tf-lock"
  }
}
