"""AWS STS."""
# Third-Party Libraries
import boto3

sts = boto3.client("sts")


def assume_role_client(self, service, role_arn):
    """Assume Role via STS."""
    resp = sts.assume_role(RoleArn=role_arn, RoleSessionName=f"{service}_session")

    return boto3.client(
        service,
        aws_access_key_id=resp["Credentials"]["AccessKeyId"],
        aws_secret_access_key=resp["Credentials"]["SecretAccessKey"],
        aws_session_token=resp["Credentials"]["SessionToken"],
    )
