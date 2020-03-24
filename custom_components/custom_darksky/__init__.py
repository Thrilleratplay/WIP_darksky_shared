"""Support for the Dark Sky weather service."""
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from darksky.api import DarkSkyAsync
from darksky.types import languages, units

import voluptuous as vol

from .const import (
    _LOGGER,
    CONF_LANGUAGE,
    CONF_UNITS,
    DARKSKY_PLATFORMS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Optional(CONF_LATITUDE): cv.latitude,
                vol.Optional(CONF_LONGITUDE): cv.longitude,
                vol.Optional(CONF_UNITS): vol.In(units.__dict__.values()),
                vol.Optional(CONF_LANGUAGE, default=languages.ENGLISH): vol.In(
                    languages.__dict__.values()
                ),
            },
        )
    },
    extra=vol.ALLOW_EXTRA,
)


# async def async_setup_entry(hass: HomeAssistant, config: Config) -> bool:
#     # We allow setup only through config
#     return True


async def async_setup(hass: HomeAssistant, config: ConfigEntry) -> bool:
    _LOGGER.error("async setup entry")
    darksky = DarkSkyData(hass, config)
    """Set up darksky forecast as config entry."""

    async def async_update_data():
        """Fetch data from API endpoint."""
        return await darksky.async_request_refresh()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Darksky Api Data",
        update_method=async_update_data,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    await coordinator.async_refresh()
    hass.data[DOMAIN] = coordinator

    for component in DARKSKY_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Unload a config entry."""
    for component in DARKSKY_PLATFORMS:
        await hass.async_create_task(
            hass.config_entries.async_forward_entry_unload(config, component)
        )
    return True


class DarkSkyData:
    def __init__(self, hass, config):
        """Initialize the data object."""
        self._hass = hass

        self._darksky = DarkSkyAsync(config[DOMAIN][CONF_API_KEY])
        self._units = config[DOMAIN].get(CONF_UNITS)

        if self._units is None and hass.config.units.is_metric:
            self._units = units.SI
        elif self._units is None:
            self._units = units.US

        lat = config[DOMAIN].get(CONF_LATITUDE, hass.config.latitude)
        long = config[DOMAIN].get(CONF_LONGITUDE, hass.config.longitude)

        self._latitude = lat
        self._longitude = long
        self._language = config[DOMAIN][CONF_LANGUAGE]

    async def async_request_refresh(self):
        """Get the latest data from Dark Sky"""
        _LOGGER.error("calling dark sky")
        return await self._darksky.get_forecast(
            self._latitude,
            self._longitude,
            lang=self._language,
            values_units=self._units,
        )
