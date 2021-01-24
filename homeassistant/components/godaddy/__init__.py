"""The GoDaddy integration. Update the IP addresses of your GoDaddy DNS records."""
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import *

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the GoDaddy component."""

    LOGGER.debug("Running GoDaddy setup")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up GoDaddy from a config entry."""
    # TODO Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    return True
