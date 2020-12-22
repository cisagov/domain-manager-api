"""Fortiguard categorization check."""
# Standard Python Libraries
import re
import urllib


def check_category(domain):
    """Check domain category on Fortiguard."""
    request = urllib.request.Request("https://fortiguard.com/webfilter?q=" + domain)
    request.add_header(
        "User-Agent", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)"
    )
    request.add_header("Origin", "https://fortiguard.com")
    request.add_header("Referer", "https://fortiguard.com/webfilter")
    response = urllib.request.urlopen(request)
    try:
        resp = response.read().decode("utf-8")
        cat = re.findall('Category: (.*?)" />', resp, re.DOTALL)
        print("\033[1;32m[!] Site categorized as: " + cat[0] + "\033[0;0m")
        return cat[0]
    except Exception as e:
        print("[-] An error occurred")
        print(e)
