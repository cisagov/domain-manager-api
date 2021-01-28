"""Main file for running tasks locally."""
# Standard Python Libraries
import json

# cisagov Libraries
from lambda_functions.check_category import handler

event = {
    "Records": [{"body": json.dumps({"domain": "google.com", "proxy": "bluecoat"})}]
}
handler(event, None)
