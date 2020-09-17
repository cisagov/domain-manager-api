"""Two Captcha utilies."""
import os
from twocaptcha import TwoCaptcha


solver = TwoCaptcha(os.environ.get("TWO_CAPTCHA"))
