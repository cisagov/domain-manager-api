"""Hugo static  site utilities."""
import os


def new_site(site_name):
    """Launch a static site with Hugo."""
    os.system(f"hugo new site {site_name}")
