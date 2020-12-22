"""Bluecoat categorization check."""
# Standard Python Libraries
import re

# Third-Party Libraries
import requests


def check_category(domain):
    """Check domain category on Bluecoat."""
    print("[*] Checking category for " + domain)
    data = {"url": domain, "captcha": ""}
    headers = {
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)",
        "Origin": "https://sitereview.bluecoat.com",
        "Referer": "https://sitereview.bluecoat.com",
        "X-Requested-With": "XMLHttpRequest",
        "X-XSRF-TOKEN": "aaa",
        "Content-Type": "application/json; charset=utf-8",
    }
    cookies = {"XSRF-TOKEN": "aaa"}
    response = requests.post(
        "http://sitereview.bluecoat.com/resource/lookup",
        headers=headers,
        json=data,
        cookies=cookies,
    )
    try:
        resp = response.text
        cat = re.findall(
            "<name>(.*?)</name></categorization></categorization>", resp, re.DOTALL
        )
        print("\033[1;32m[!] Site categorized as: " + cat[0] + "\033[0;0m")
        return cat[0]
    except Exception as e:
        print("[-] An error occurred")
        print(e)
