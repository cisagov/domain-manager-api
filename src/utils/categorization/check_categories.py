"""Check categories."""
from argparse import ArgumentParser
import argparse
import sys
import os
from utils.modules import (
    bluecoat,
    ciscotalos,
    expireddomfilter,
    fortiguard,
    ibmxforce,
    trustedsource,
    websense,
)
import urllib
import re


def check_trustedsource(domain):
    """Trusted source check."""
    print("\033[1;34m[*] Targeting McAfee Trustedsource\033[0;0m")
    return trustedsource.check_category(domain)


def check_bluecoat(domain):
    """Bluecoat check."""
    print("\033[1;34m[*] Targeting Bluecoat WebPulse\033[0;0m")
    return bluecoat.check_category(domain)


def check_ibm(domain):
    """IBM check."""
    print("\033[1;34m[*] Targeting IBM Xforce\033[0;0m")
    xf = ibmxforce.IBMXforce()
    return xf.checkIBMxForce(domain)


def check_fortiguard(domain):
    """Fortiguard check."""
    print("\033[1;34m[*] Targeting Fortiguard\033[0;0m")
    xf = fortiguard.Fortiguard()
    return xf.check_category(domain)


def check_websense(domain):
    """Websense check."""
    print("\033[1;34m[*] Targeting Websense\033[0;0m")
    xf = websense.Websense()
    return xf.check_category(domain)


def check_cisco(domain):
    """Cisco check."""
    print("\033[1;34m[*] Targeting Cisco Talos\033[0;0m")
    xf = ciscotalos.CiscoTalos()
    xf.check_category(domain)


def expired_search(filename, argfilter):
    """Expired search check."""
    es = expireddomfilter.ExpiredDom()
    es.check_filter(filename, argfilter)
