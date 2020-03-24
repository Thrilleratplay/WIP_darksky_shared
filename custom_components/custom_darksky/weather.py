"""Support for displaying weather info from Dark Sky API."""
import voluptuous as vol
from homeassistant.util.pressure import convert as convert_pressure
import homeassistant.helpers.config_validation as cv

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    PLATFORM_SCHEMA,
    WeatherEntity,
)
from homeassistant.const import (
    CONF_MODE,
    CONF_NAME,
    PRESSURE_HPA,
    PRESSURE_INHG,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

from darksky.types import units

from .const import (
    _LOGGER,
    DEFAULT_NAME,
    DEFAULT_MODE,
    DOMAIN,
    FORECAST_MODE,
    ATTRIBUTION,
    MAP_CONDITION,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_MODE, default=DEFAULT_MODE): vol.In(FORECAST_MODE),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Dark Sky weather platform."""
    data = hass.data[DOMAIN]

    async_add_entities([DarkSkyWeather(data, config[CONF_MODE])], True)

    return True


def imperial_pressure(pressure):
    return round(convert_pressure(pressure, PRESSURE_HPA, PRESSURE_INHG), 2)


class DarkSkyWeather(WeatherEntity):
    """Representation of an weather sensor."""

    def __init__(self, coordinator, mode):
        """Initialize Dark Sky weather."""

        _LOGGER.debug("Initializing DarkSky Weather sensor")

        self._name = DEFAULT_NAME
        self._coordinator = coordinator
        self._mode = mode

        self._currently = coordinator.data.currently
        self._hourly = coordinator.data.hourly
        self._daily = coordinator.data.daily
        self._flags = coordinator.data.flags

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
        if self._flags.units == units.US:
            return TEMP_FAHRENHEIT
        else:
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
        if self._flags.units == units.US:
            return imperial_pressure(self._currently.pressure)
        else:
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

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self._coordinator.update_method()

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self._coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Undo subscription."""
        self._coordinator.async_remove_listener(self.async_write_ha_state)

    @property
    def forecast(self):
        """Return the forecast array."""
        # Per conversation with Joshua Reyes of Dark Sky, to get the total
        # forecasted precipitation, you have to multiple the intensity by
        # the hours for the forecast interval
        def calc_precipitation(intensity, hours):
            amount = None
            if intensity is not None:
                amount = round((intensity * hours), 1)
            return amount if amount > 0 else None

        data = None

        if self._mode == "daily" and self._daily.data is not None:
            data = [
                {
                    ATTR_FORECAST_TIME: entry.time.isoformat(),
                    ATTR_FORECAST_TEMP: entry.temperature_high,
                    ATTR_FORECAST_TEMP_LOW: entry.temperature_low,
                    ATTR_FORECAST_PRECIPITATION: calc_precipitation(
                        entry.precip_intensity, 24
                    ),
                    ATTR_FORECAST_WIND_SPEED: entry.wind_speed,
                    ATTR_FORECAST_WIND_BEARING: entry.wind_bearing,
                    ATTR_FORECAST_CONDITION: MAP_CONDITION.get(entry.icon),
                }
                for entry in self._daily.data
            ]
        elif self._mode == "hourly" and self._hourly.data is not None:
            data = [
                {
                    ATTR_FORECAST_TIME: entry.time.isoformat(),
                    ATTR_FORECAST_TEMP: entry.temperature,
                    ATTR_FORECAST_PRECIPITATION: calc_precipitation(
                        entry.precip_intensity, 1
                    ),
                    ATTR_FORECAST_CONDITION: MAP_CONDITION.get(entry.icon),
                }
                for entry in self._hourly.data
            ]

        return data
