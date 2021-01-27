"""Constants for the GoDaddy integration."""

import logging

DOMAIN = "godaddy"
LOGGER = logging.getLogger(__name__)

GODADDY_API_BASE_URL = "https://api.godaddy.com"
GODADDY_DOMAINS_API = GODADDY_API_BASE_URL + "/v1/domains"

IPIFY_URL = "https://api.ipify.org/"

CONF_ENTRY_NAME = "GoDaddy"
CONF_API_KEY = "api_key"
CONF_API_SECRET = "api_secret"

SERVICE_NAME = "update_dns_record"
