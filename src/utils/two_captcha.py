"""Two Captcha utilies."""
import os
from twocaptcha import TwoCaptcha


two_captcha_api_key = os.environ.get("TWO_CAPTCHA")
solver = TwoCaptcha(two_captcha_api_key)
