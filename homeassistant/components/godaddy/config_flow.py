"""Config flow for GoDaddy integration."""
from homeassistant.helpers import aiohttp_client
import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions

from .const import *  # pylint:disable=unused-import

STEP_USER_DATA_SCHEMA = vol.Schema({"entry_name": str, "api_key": str, "api_secret": str})

async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    session = aiohttp_client.async_create_clientsession(hass, auto_cleanup=False)

    url = "https://api.godaddy.com/v1/domains"
    headers = {
        "Authorization": "sso-key"
    }
    headers[data["api_key"]]= data["api_secret"]
    LOGGER.warn("Headers: %s", headers)
    domains_request = await session.get(url, headers=headers)
    domains_result = await domains_request.json()
    LOGGER.debug("Received domains response: %s", domains_result)

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    return


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GoDaddy."""

    VERSION = 1
    # Unknown connection class, since integration is not observing any state
    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
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
            return self.async_create_entry(title=user_input["entry_name"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
