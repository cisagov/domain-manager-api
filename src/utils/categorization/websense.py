"""Websense categorization check."""
# Standard Python Libraries
import re
import sys
import urllib

# Third-Party Libraries
from bs4 import BeautifulSoup


def req_check():
    """Check requests for the day."""
    request = urllib.request.Request("http://csi.websense.com")
    request.add_header(
        "User-Agent", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)"
    )
    response = urllib.request.urlopen(request)
    resp = response.read().decode("utf-8")
    num_remaining = re.findall('reports">(.*?) report', resp, re.DOTALL)[0]
    return num_remaining


def check_category(domain):
    """Check domain category on Websense."""
    num_remaining = req_check()
    print("[-] You have " + num_remaining + " requests left for the day.")
    if int(num_remaining) > 0:
        print("[*] Checking category for " + domain)
        request = urllib.request.Request("http://csi.websense.com")
        data = urllib.parse.urlencode({"LookupUrl": domain})
        data = data.encode("utf-8")
        request.add_header(
            "User-Agent", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)"
        )
        response = urllib.request.urlopen(request, data=data)
        try:
            resp = response.read().decode("utf-8")
            location = re.findall('<td class="classAction">(.*?)</td>', resp, re.DOTALL)
            cat = location[2]
            print("\033[1;32m[!] Site categorized as: " + cat + "\033[0;0m")
            return cat
        except Exception as e:
            print("[-] An error occurred")
            print(e)
    else:
        print("[-] No requests remaining for this IP.")
