import re
import ssl
import socket
from typing import Dict
from urllib.parse import urlparse
import whois
from datetime import datetime

def check_ssl_state(url: str) -> int:
    """
    Check the SSL/TLS state of the given URL.
    Returns:
    - 1: Valid HTTPS with an SSL certificate.
    - 0: HTTPS but invalid/expired SSL certificate.
    - -1: HTTP or no SSL/TLS.
    """
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc

    # Default to no SSL
    if not parsed_url.scheme.startswith("https"):
        return -1

    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # SSL is valid if no exception occurs
                return 1
    except Exception:
        # SSL/TLS failed
        return 0

def check_domain_registration_length(url: str) -> int:
    """
    Check the domain registration length of the given URL.
    Returns:
    - 1: More than 1 year left.
    - 0: Less than or equal to 1 year left.
    - -1: Error in fetching registration details.
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        domain_info = whois.whois(domain)

        # Check expiration date
        expiration_date = domain_info.expiration_date
        if isinstance(expiration_date, list):  # Some whois services return a list
            expiration_date = expiration_date[0]

        if expiration_date:
            remaining_days = (expiration_date - datetime.now()).days
            return 1 if remaining_days > 365 else 0
        return -1  # No expiration date found
    except Exception:
        return -1  # Error in fetching WHOIS data


# Feature extraction logic
def extract_features(url: str):
    """
    Extract features from the input URL.
    Replace this logic with your actual feature extraction implementation.
    """
    features = {
        "having_IP_Address": 1 if re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', url) else -1,
        "URL_Length": len(url),
        "Shortining_Service": 1 if "bit.ly" in url or "t.co" in url else -1,
        "having_At_Symbol": 1 if "@" in url else -1,
        "double_slash_redirecting": 1 if "//" in url[7:] else -1,
        "Prefix_Suffix": 1 if "-" in url else -1,
        "having_Sub_Domain": 1 if url.count('.') > 2 else 0 if url.count('.') == 2 else -1,
        "SSLfinal_State": check_ssl_state(url),
        "Domain_registeration_length": check_domain_registration_length(url),
    }
    return features