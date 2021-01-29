"""The GoDaddy integration. Update the IP addresses of your GoDaddy DNS records."""
from homeassistant.const import ATTR_DOMAIN
from homeassistant.helpers import aiohttp_client
import aiohttp

from homeassistant import exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import tldextract

from .const import *


class GoDaddyAPI:
    """Makes GoDaddy API calls"""

    def __init__(
        self, session: aiohttp.ClientSession, api_key: str, api_secret: str
    ) -> None:
        """Initializes the GoDaddy API"""

        self.session = session
        self.headers = {"Authorization": "sso-key %s:%s" % (api_key, api_secret)}

    async def validateAPIKey(self) -> None:
        domains_request = await self.session.get(
            GODADDY_DOMAINS_API, headers=self.headers
        )
        domains_request.close()

        if domains_request.status != 200:
            raise InvalidAuth

    async def updateARecord(self, registered_domain_name: str, subdomain: str, ip: str) -> None:
        if not subdomain:
            subdomain = "@"

        put_a_record_url = "%s/%s/records/A/%s" % (
            GODADDY_DOMAINS_API,
            registered_domain_name,
            subdomain,
        )
        put_a_record_body = [{"data": ip}]
        put_a_record_request = await self.session.put(
            put_a_record_url, headers=self.headers, json=put_a_record_body
        )

        if put_a_record_request.status != 200:
            put_a_record_response = await put_a_record_request.text()
            LOGGER.error(
                "Error updating A record for domain: %s%s - Error: %s",
                subdomain,
                registered_domain_name,
                put_a_record_response,
            )
        else:
            put_a_record_request.close()


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the GoDaddy component."""

    return True


async def get_external_ip(session: aiohttp.ClientSession) -> str:
    ipify_request = await session.get(IPIFY_URL)
    ipify_response = await ipify_request.text()
    LOGGER.debug("Received external IP from ipify.org: %s", ipify_response)

    return ipify_response


async def update_dns_record(
    hass: HomeAssistant, godaddyAPI: GoDaddyAPI, session: aiohttp.ClientSession, domain: str
) -> None:
    if domain is None:
        LOGGER.error(
            "Domain is not specified. Please ensure that you are calling the service correctly and pass your domain with the %s property.",
            ATTR_DOMAIN,
        )
        return

    LOGGER.info("Updating DNS record for domain: %s", domain)

    # Get external IP
    external_ip = await get_external_ip(session)

    # split subdomain and domain name
    domain_parts = await hass.async_add_executor_job(tldextract.extract, domain)
    registered_domain_name = domain_parts.registered_domain
    subdomain = domain_parts.subdomain

    # Update DNS record for domain
    await godaddyAPI.updateARecord(registered_domain_name, subdomain, external_ip)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up GoDaddy from a config entry."""

    LOGGER.debug("Registering GoDaddy update DNS records service")

    godaddyAPI = GoDaddyAPI(
        aiohttp_client.async_get_clientsession(hass),
        entry.data[CONF_API_KEY],
        entry.data[CONF_API_SECRET],
    )

    async def handle_update_dns_record(call):
        await update_dns_record(
            hass,
            godaddyAPI,
            aiohttp_client.async_get_clientsession(hass),
            call.data.get(ATTR_DOMAIN),
        )

    hass.services.async_register(DOMAIN, SERVICE_NAME, handle_update_dns_record)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    LOGGER.debug("Unregistering GoDaddy update DNS records service")

    hass.services.async_remove(DOMAIN, SERVICE_NAME)

    return True


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
