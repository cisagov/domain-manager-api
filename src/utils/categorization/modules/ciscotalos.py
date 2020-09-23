"""Cisco Talos categorization check."""
import requests
import sys
import re
from bs4 import BeautifulSoup
import json


def check_category(domain):
    """Check domain category on Cisco Talos."""
    print("[*] Checking category for " + domain)
    response = requests.get(
        f"https://talosintelligence.com/sb_api/query_lookup?query=%2Fapi%2Fv2%2Fdetails%2Fdomain%2F&query_entry={domain}&offset=0&order=ip+asc",
        headers={
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)",
            "Referer": f"https://www.talosintelligence.com/reputation_center/lookup?search={domain}",
        },
    )
    try:
        check_json = json.loads(response.read())
        categorydict = check_json.get("category")
        cat = categorydict.get("description")
        print("\033[1;32m[!] Site categorized as: " + cat + "\033[0;0m")
        return cat
    except Exception as e:
        print("[-] An error occurred")
        print(e)
