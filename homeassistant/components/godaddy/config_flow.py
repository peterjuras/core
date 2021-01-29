"""Config flow for GoDaddy integration."""

from . import GoDaddyAPI, InvalidAuth
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.helpers import aiohttp_client

from .const import (
    DOMAIN,
    LOGGER,
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_ENTRY_NAME,
)


def _schema_with_defaults(api_key: str = None, api_secret: str = None):
    return vol.Schema(
        {
            vol.Required(CONF_API_KEY, default=api_key): str,
            vol.Required(CONF_API_SECRET, default=api_secret): str,
        }
    )


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect to the GoDaddy API"""

    godaddyAPI = GoDaddyAPI(
        aiohttp_client.async_get_clientsession(hass),
        data["api_key"],
        data["api_secret"],
    )
    await godaddyAPI.validateAPIKey()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GoDaddy."""

    VERSION = 1
    # Unknown connection class, since integration is not observing any state
    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=_schema_with_defaults()
            )

        errors = {}

        try:
            await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=CONF_ENTRY_NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema_with_defaults(
                user_input[CONF_API_KEY],
                user_input[CONF_API_SECRET],
            ),
            errors=errors,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
