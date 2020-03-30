"""Support for the Dark Sky weather service."""
import voluptuous as vol
import logging
from darksky.api import DarkSkyAsync  # pylint: disable=import-error
from darksky.types import languages, units  # pylint: disable=import-error

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_LANGUAGE,
    CONF_UNITS,
    DARKSKY_PLATFORMS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .shared import format_daily_forecast, format_hourly_forecast

_LOGGER = logging.getLogger(__name__)

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


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up Darksky as config entries."""
    for component in DARKSKY_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config, component)
        )
    return True


async def async_setup(hass: HomeAssistant, config: ConfigEntry):
    """Set up configured Darksky."""
    darksky = DarkSkyData(hass, config)

    hass.data[DOMAIN] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Darksky Api Data",
        update_method=darksky.async_request_refresh,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    await hass.data[DOMAIN].async_refresh()

    return True


async def async_unload_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Unload a config entry."""
    for component in DARKSKY_PLATFORMS:
        await hass.async_create_task(
            hass.config_entries.async_forward_entry_unload(config, component)
        )
    return True


class DarkSkyData:
    """DarkSky API request."""

    def __init__(self, hass, config):
        """Initialize the data object."""
        lat = config[DOMAIN].get(CONF_LATITUDE, hass.config.latitude)
        long = config[DOMAIN].get(CONF_LONGITUDE, hass.config.longitude)

        self._hass = hass
        self._darksky = DarkSkyAsync(config[DOMAIN][CONF_API_KEY])
        self._units = config[DOMAIN].get(CONF_UNITS)
        self._latitude = lat
        self._longitude = long
        self._language = config[DOMAIN][CONF_LANGUAGE]

        if self._units is None and hass.config.units.is_metric:
            self._units = units.SI
        elif self._units is None:
            self._units = units.US

    async def async_request_refresh(self):
        """Get the latest data from Dark Sky."""
        try:
            res = await self._darksky.get_forecast(
                self._latitude,
                self._longitude,
                lang=self._language,
                values_units=self._units,
            )
            res.ha_daily_forecast = format_daily_forecast(res.daily.data)
            res.ha_hourly_forecast = format_hourly_forecast(res.hourly.data)
            res.units = res.flags.units
            return res
        except LookupError:
            raise UpdateFailed("Failed to fetch data")
