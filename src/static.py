import os

AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
TEMPLATE_BUCKET = os.environ["TEMPLATE_BUCKET"]
TEMPLATE_BUCKET_URL = f"http://{TEMPLATE_BUCKET}.s3-website-{AWS_REGION}.amazonaws.com/"
