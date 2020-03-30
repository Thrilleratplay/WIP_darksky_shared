"""Support for displaying weather info from Dark Sky API."""
import voluptuous as vol
import logging
from darksky.types import units  # pylint: disable=import-error

import homeassistant.helpers.config_validation as cv
from homeassistant.components.weather import (
    PLATFORM_SCHEMA,
    WeatherEntity,
)
from homeassistant.const import (
    CONF_MODE,
    CONF_NAME,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

from .const import (
    DEFAULT_NAME,
    DEFAULT_MODE,
    DOMAIN,
    FORECAST_MODE,
    ATTRIBUTION,
    MAP_CONDITION,
)
from .shared import imperial_pressure

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_MODE, default=DEFAULT_MODE): vol.In(FORECAST_MODE),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Dark Sky weather platform."""
    coordinator = hass.data[DOMAIN]
    mode = config[CONF_MODE]
    async_add_entities([DarkSkyWeather(coordinator, mode)], True)
    return True


class DarkSkyWeather(WeatherEntity):
    """Representation of an weather sensor."""

    def __init__(self, coordinator, mode):
        """Initialize Dark Sky weather."""

        _LOGGER.debug("Initializing DarkSky Weather sensor")

        self._name = DEFAULT_NAME
        self._mode = mode
        self._coordinator = coordinator
        self._currently = coordinator.data.currently
        self._units = coordinator.data.units

    @property
    def available(self):
        """Return if weather data is available from Dark Sky."""
        return self._coordinator.last_update_success

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def temperature(self):
        """Return the temperature."""
        return self._currently.temperature

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        if self._units == units.US:
            return TEMP_FAHRENHEIT
        return TEMP_CELSIUS

    @property
    def humidity(self):
        """Return the humidity."""
        humidity = self._currently.humidity
        return round(humidity * 100.0, 2)

    @property
    def wind_speed(self):
        """Return the wind speed."""
        return self._currently.wind_speed

    @property
    def wind_bearing(self):
        """Return the wind bearing."""
        return self._currently.wind_bearing

    @property
    def ozone(self):
        """Return the ozone level."""
        return self._currently.ozone

    @property
    def pressure(self):
        """Return the pressure."""
        if self._units == units.US:
            return imperial_pressure(self._currently.pressure)
        return self._currently.pressure

    @property
    def visibility(self):
        """Return the visibility."""
        return self._currently.visibility

    @property
    def condition(self):
        """Return the weather condition."""
        return MAP_CONDITION.get(self._currently.icon)

    @property
    def should_poll(self):
        """Return False, updates are controlled via coordinator."""
        return False

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._name}_weather"

    @property
    def forecast(self):
        """Return the forecast array."""
        if self._mode == "hourly":
            return self._coordinator.data.ha_hourly_forecast
        if self._mode == "daily":
            return self._coordinator.data.ha_daily_forecast

        return None

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self._coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Undo subscription."""
        self._coordinator.async_remove_listener(self.async_write_ha_state)
