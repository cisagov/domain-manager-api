"""
Regional Endpoints for S3.

There is not an API for this information and thus has to be hardcoded. The values can be found at https://docs.aws.amazon.com/general/latest/gr/s3.html.
"""
# cisagov Libraries
from settings import AWS_REGION

REGIONAL_ENDPOINTS = {
    "us-east-1": {
        "website_endpoint": "s3-website-us-east-1.amazonaws.com",
        "hosted_zone_id": "Z3AQBSTGFYJSTF",
    },
    "us-east-2": {
        "website_endpoint": "s3-website-us-east-2.amazonaws.com",
        "hosted_zone_id": "Z2O1EMRO9K5GLX",
    },
    "us-west-1": {
        "website_endpoint": "s3-website-us-west-1.amazonaws.com",
        "hosted_zone_id": "Z2F56UZL2M1ACD ",
    },
    "us-west-2": {
        "website_endpoint": "s3-website-us-west-2.amazonaws.com",
        "hosted_zone_id": "Z3BJ6K6RIION7M",
    },
    "us-gov-east-1": {
        "website_endpoint": "s3-website-us-gov-east-1.amazonaws.com",
        "hosted_zone_id": "Z2NIFVYYW2VKV1 ",
    },
    "us-gov-west-1": {
        "website_endpoint": "s3-website-us-gov-west-1.amazonaws.com",
        "hosted_zone_id": "Z31GFT0UA1I2HV",
    },
}


REGIONAL_WEBSITE_ENDPOINT = REGIONAL_ENDPOINTS[AWS_REGION]["website_endpoint"]

REGIONAL_HOSTED_ZONE_ID = REGIONAL_ENDPOINTS[AWS_REGION]["hosted_zone_id"]
