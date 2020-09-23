"""Fortiguard categorization check."""
import requests
import re
from bs4 import BeautifulSoup
import json


def check_category(domain):
    """Check domain category on Fortiguard."""
    print("[*] Checking category for " + domain)
    response = requests.get(
        f"https://fortiguard.com/webfilter?q={domain}",
        headers={
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)",
            "Origin": "https://fortiguard.com",
            "Referer": "https://fortiguard.com/webfilter",
        },
    )
    try:
        resp = response.read().decode("utf-8")
        cat = re.findall('Category: (.*?)" />', resp, re.DOTALL)
        print("\033[1;32m[!] Site categorized as: " + cat[0] + "\033[0;0m")
        return cat[0]
    except Exception as e:
        print("[-] An error occurred")
        print(e)
