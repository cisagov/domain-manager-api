"""Receive Emails Lambda Function."""
# Standard Python Libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Third-Party Libraries
from botocore.exceptions import ClientError

# cisagov Libraries
from api.main import app
from api.manager import DomainManager, EmailManager
from api.settings import Settings
from utils.aws.clients import SES

logger = logging.getLogger()
logger.setLevel(logging.INFO)

domain_manager = DomainManager()
email_manager = EmailManager()
ses = SES()
settings = Settings()


def forward_email(message):
    """Forward an Email to specified email address."""
    settings.load()
    forward_address = settings.to_dict()["SES_FORWARD_EMAIL"]
    logger.info("forward to: ", forward_address)

    msg = MIMEMultipart()
    text_part = MIMEText(message["message"], _subtype="html")
    msg.attach(text_part)

    # Add subject, from, and to
    msg["Subject"] = message["subject"]
    msg["From"] = message["from_address"]
    msg["To"] = message["to_address"]

    try:
        response = ses.client.send_raw_email(
            Source=message["from_address"],
            Destinations=[forward_address],
            RawMessage={"Data": msg.as_string()},
        )
    except ClientError as e:
        logger.error(e.response["Error"]["Message"])

    return response


def lambda_handler(event, context):
    """Lambda Handler."""
    incoming = event["Records"][0]["ses"]["mail"]
    target_email = incoming["destination"][0]
    domain = domain_manager.get(filter_data={"name": target_email.split("@")[1]})

    if not domain:
        logger.info(incoming)
        logger.error(f"domain from {target_email} does not exist")
        return

    data = {
        "domain_id": domain["_id"],
        "timestamp": incoming["timestamp"],
        "from_address": incoming["commonHeaders"]["from"][0],
        "to_address": incoming["commonHeaders"]["to"][0],
        "subject": incoming["commonHeaders"]["subject"],
        "message": "<p>Not yet available.</p>",
    }
    logger.info(data)

    with app.app_context():
        email_manager.save(data)

    logger.info("success")


if __name__ == "__main__":
    lambda_handler(None, None)
