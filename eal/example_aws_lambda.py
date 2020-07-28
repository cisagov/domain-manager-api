#!/usr/bin/env python3

"""example_aws_lambda: An example AWS lambda for the cisagov organization.

Usage:
  eal --region REGION --message MESSAGE [--log-level=LEVEL]
  eal (-h | --help)
  eal --version

Options:
  -h --help                   Show this message.
  --version                   Show version.
  --region REGION             The region this is running in.
  --message MESSAGE           The message to output.
  --log-level=LEVEL           If specified, then the log level will be set to
                              the specified value.  Valid values are "debug",
                              "info", "warning", "error", and "critical".
                              [default: warning]
"""

# Standard Python Libraries
from datetime import datetime, timezone
import logging

# Third-Party Libraries
import docopt


# Local library
from ._version import __version__


def setup_logging(log_level):
    """Set up logging at the provided level."""
    try:
        logging.basicConfig(
            format="%(asctime)-15s %(levelname)s %(message)s", level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            f'"{log_level}" is not a valid logging level.  Possible values '
            "are debug, info, warning, error, and critical."
        )
        return 1


def do_lambda_functionality(region=None, invocation_time=None, message="Hello, World!"):
    """Print out the provided region, invocation time, and the function's time."""
    function_time = datetime.now(timezone.utc)

    logging.debug(__name__)
    print(f"Region: {region}")
    print(f"Invocation Time: {invocation_time}")
    print(f"Function Time (UTC): {function_time}")
    print(f"Provided Message: {message}")

    return True


def main():
    """Set up logging and call the import_data function."""
    # Parse command line arguments
    args = docopt.docopt(__doc__, version=__version__)

    # Set up logging
    setup_logging(args["--log-level"])

    result = do_lambda_functionality(
        args["--region"], datetime.now(timezone.utc), args["--message"]
    )

    # Stop logging and clean up
    logging.shutdown()

    return 0 if result else -1


if __name__ == "__main__":
    main()
