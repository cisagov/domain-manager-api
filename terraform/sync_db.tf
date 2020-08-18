# ===================================
# Lambda Layer
# ===================================
data "archive_file" "layer" {
  type        = "zip"
  source_dir  = "${path.module}/layer"
  output_path = "${path.module}/output/layer.zip"
}

resource "aws_lambda_layer_version" "layer" {
  filename         = data.archive_file.layer.output_path
  source_code_hash = data.archive_file.layer.output_path
  layer_name       = "${var.app}-${var.env}-layer"

  compatible_runtimes = ["python3.8"]
}

# ===================================
# Lambda Function
# ===================================
data "archive_file" "sync_db" {
  type        = "zip"
  source_file = "${path.module}/../src/lambda_functions/sync_db.py"
  output_path = "${path.module}/output/sync_db.zip"
}

resource "aws_lambda_function" "sync_db" {
  filename         = data.archive_file.sync_db.output_path
  function_name    = "${var.app}-${var.env}-sync_db"
  handler          = "sync_db.lambda_handler"
  layers           = [aws_lambda_layer_version.layer.arn]
  role             = aws_iam_role.lambda_exec_role.arn
  memory_size      = 128
  runtime          = "python3.8"
  source_code_hash = data.archive_file.sync_db.output_base64sha256
  timeout          = 300

  environment {
    variables = local.environment
  }

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.api.id]
  }
}

# ===================================
# IAM Roles
# ===================================
resource "aws_iam_role" "lambda_exec_role" {
  name               = "lambda_exec_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      }
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    sid    = "AllowCreatingLogGroups"
    effect = "Allow"

    resources = [
      "arn:aws:logs:*:*:*"
    ]

    actions = [
      "logs:CreateLogGroup"
    ]
  }

  statement {
    sid    = "AllowWritingLogs"
    effect = "Allow"

    resources = [
      "arn:aws:logs:*:*:log-group:/aws/lambda/*:*"
    ]

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
  }

  statement {
    sid = "Allow Attaching to VPC"
    effect = "Allow"
    
    resources = [
      "*"
    ]

    actions = [
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DeleteNetworkInterface"
    ]
  }
}

resource "aws_iam_policy" "lambda_iam_policy" {
  name   = "lambda_iam_policy"
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  policy_arn = aws_iam_policy.lambda_iam_policy.arn
  role       = aws_iam_role.lambda_exec_role.name
}
