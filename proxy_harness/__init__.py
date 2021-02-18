"""Initialize proxy harnass."""
# Standard Python Libraries
import os
import sys

# Third-Party Libraries
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(f"{script_dir}/../src"))

load_dotenv(dotenv_path=f"{script_dir}/../.env")
