"""Support for Dark Sky weather service."""
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    SPEED_KILOMETERS_PER_HOUR,
    SPEED_METERS_PER_SECOND,
    SPEED_MILES_PER_HOUR,
    TIME_HOURS,
    UNIT_PERCENTAGE,
    UNIT_UV_INDEX,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from darksky.types import units

from .const import (
    _LOGGER,
    DEFAULT_NAME,
    ATTRIBUTION,
    DOMAIN,
    ICONS,
    CONF_FORECAST,
    CONF_HOURLY_FORECAST,
    DEPRECATED_SENSOR_TYPES,
    CONDITION_PICTURES,
    CURRENTLY_SENSOR,
    DAILY_SENSOR,
    HOURLY_SENSOR,
    ALERTS_ATTRS,
    SENSOR_LABELS,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MONITORED_CONDITIONS): vol.All(
            cv.ensure_list, [vol.In(SENSOR_LABELS)]
        ),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_FORECAST): vol.All(cv.ensure_list, [vol.Range(min=0, max=7)]),
        vol.Optional(CONF_HOURLY_FORECAST): vol.All(
            cv.ensure_list, [vol.Range(min=0, max=48)]
        ),
    }
)


# https://stackoverflow.com/a/1034598
def xstr(s):
    """ Return string or empty string if None """
    return "" if s is None else str(s)


def unit_of_measurement(sensor_type, unit_type):
    """Return unit of a given measurement for unit type """
    if sensor_type in ["nearest_storm_distance", "visibility"]:
        return "mi" if unit_type in [units.US, units.UK2] else "km"
    elif sensor_type in ["precip_intensity", "precip_intensity_max"]:
        return "in" if unit_type == units.US else f"mm/{TIME_HOURS}"
    elif sensor_type in [
        "temperature",
        "apparent_temperature",
        "dew_point",
        "apparent_temperature_max",
        "apparent_temperature_high",
        "apparent_temperature_min",
        "apparent_temperature_low",
        "temperature_max",
        "temperature_high",
        "temperature_min",
        "temperature_low",
    ]:
        return "°F" if unit_type == units.US else "°C"
    elif sensor_type in ["wind_speed", "wind_gust"]:
        if unit_type in [units.US, units.UK2]:
            return SPEED_MILES_PER_HOUR
        elif unit_type == units.CA:
            return SPEED_KILOMETERS_PER_HOUR
        else:
            return SPEED_METERS_PER_SECOND
    elif sensor_type in ["precip_probability", "cloud_cover", "humidity"]:
        return UNIT_PERCENTAGE
    elif sensor_type == "pressure":
        return "mbar"
    elif sensor_type == "ozone":
        return "DU"
    elif sensor_type == "uv_index":
        return UNIT_UV_INDEX
    elif sensor_type == "precip_accumulation":
        return "in" if unit_type == units.US else "cm"
    elif sensor_type in ["nearest_storm_bearing", "wind_bearing"]:
        return "°"
    else:
        return None


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Dark Sky weather platform."""
    data = hass.data[DOMAIN]

    name = config[CONF_NAME]

    forecast = config[CONF_FORECAST]
    forecast_hour = config[CONF_HOURLY_FORECAST]
    sensors = []

    for variable in config[CONF_MONITORED_CONDITIONS]:

        if variable in DEPRECATED_SENSOR_TYPES:
            _LOGGER.warning("Monitored condition %s is deprecated", variable)

        if variable == "alerts":
            sensors.append(DarkSkyAlertSensor(data, variable, name))
        else:
            if variable in CURRENTLY_SENSOR:
                sensors.append(DarkSkySensor(data, variable, name))

            if forecast is not None and variable in DAILY_SENSOR:
                for forecast_day in forecast:
                    sensors.append(
                        DarkSkySensor(data, variable, name, forecast_day=forecast_day)
                    )

            if forecast_hour is not None and variable in HOURLY_SENSOR:
                for forecast_h in forecast_hour:
                    sensors.append(
                        DarkSkySensor(data, variable, name, forecast_hour=forecast_h)
                    )
    _LOGGER.error(sensors)
    async_add_entities(sensors, True)


class DarkSkySensor(Entity):
    """Implementation of a Dark Sky sensor."""

    def __init__(
        self, coordinator, sensor_type, name, forecast_day=None, forecast_hour=None
    ):
        """Initialize the sensor."""
        self.client_name = name
        self._name = SENSOR_LABELS[sensor_type]
        self._currently = coordinator.data.currently
        self._hourly = coordinator.data.hourly
        self._daily = coordinator.data.daily
        self._flags = coordinator.data.flags
        self.type = sensor_type
        self.forecast_day = forecast_day
        self.forecast_hour = forecast_hour
        self._state = None
        self._icon = None
        self._unit_of_measurement = None

    @property
    def name(self):
        """Return the name of the sensor."""
        if self.forecast_day is not None:
            return f"{self.client_name} {self._name} {self.forecast_day}d"
        if self.forecast_hour is not None:
            return f"{self.client_name} {self._name} {self.forecast_hour}h"
        return f"{self.client_name} {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def unit_system(self):
        """Return the unit system of this entity."""
        return self.forecast_data.unit_system

    @property
    def entity_picture(self):
        """Return the entity picture to use in the frontend, if any."""
        if self._icon is None or "summary" not in self.type:
            return None

        if self._icon in CONDITION_PICTURES:
            return CONDITION_PICTURES[self._icon]

        return None

    def update_unit_of_measurement(self):
        """Update units based on unit system."""
        units = self._flags.units
        if units is not None:
            self._unit_of_measurement = unit_of_measurement(self.type, units)
        else:
            self._unit_of_measurement = None

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if "summary" in self.type and self._icon in ICONS:
            return ICONS[self._icon]

        return ICONS[self.type]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {ATTR_ATTRIBUTION: ATTRIBUTION}

    async def async_update(self):
        """Get the latest data from Dark Sky and updates the states."""
        self.update_unit_of_measurement()

        if self.type == "minutely_summary":
            self._state = xstr(self._currently.summary)
            self._icon = xstr(self._currently.icon)
        elif self.type == "hourly_summary":
            self._state = xstr(self._hourly.data[0].summary)
            self._icon = xstr(self._hourly.data[0].icon)
        elif self.type == "daily_summary":
            self._state = xstr(self._daily.data[0].summary)
            self._icon = xstr(self._daily.data[0].icon)
        elif self.forecast_hour is not None:
            hourly = self._hourly
            if hasattr(hourly, "data"):
                self._state = self.get_state(hourly.data[self.forecast_hour])
            else:
                self._state = 0
        elif self.forecast_day is not None:
            daily = self._daily
            if hasattr(daily, "data"):
                self._state = self.get_state(daily.data[self.forecast_day])
            else:
                self._state = 0
        else:
            self._state = self.get_state(self._currently)

    def get_state(self, data):
        """
        Return a new state based on the type.

        If the sensor type is unknown, the current state is returned.
        """
        state = getattr(data, self.type, None)

        if state is None:
            return state

        if "summary" in self.type:
            self._icon = getattr(data, "icon", "")

        # Some state data needs to be rounded to whole values or converted to
        # percentages
        if self.type in ["precip_probability", "cloud_cover", "humidity"]:
            return round(state * 100, 1)

        if self.type in [
            "dew_point",
            "temperature",
            "apparent_temperature",
            "temperature_low",
            "apparent_temperature_low",
            "temperature_min",
            "apparent_temperature_min",
            "temperature_high",
            "apparent_temperature_high",
            "temperature_max",
            "apparent_temperature_max",
            "precip_accumulation",
            "pressure",
            "ozone",
            "uvIndex",
        ]:
            return round(state, 1)
        return state


class DarkSkyAlertSensor(Entity):
    """Implementation of a Dark Sky sensor."""

    def __init__(self, forecast_data, sensor_type, name):
        """Initialize the sensor."""
        self.client_name = name
        self._name = SENSOR_LABELS[sensor_type]
        self.forecast_data = forecast_data
        self.type = sensor_type
        self._state = None
        self._icon = None
        self._alerts = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.client_name} {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._state is not None and self._state > 0:
            return "mdi:alert-circle"
        return "mdi:alert-circle-outline"

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._alerts

    async def async_update(self):
        """Get the latest data from Dark Sky and updates the states."""
        self.forecast_data.update()
        self.forecast_data.update_alerts()
        alerts = self.forecast_data.data_alerts
        self._state = self.get_state(alerts)

    def get_state(self, data):
        """
        Return a new state based on the type.

        If the sensor type is unknown, the current state is returned.
        """
        alerts = {}
        if data is None:
            self._alerts = alerts
            return data

        multiple_alerts = len(data) > 1
        for i, alert in enumerate(data):
            for attr in ALERTS_ATTRS:
                if multiple_alerts:
                    dkey = f"{attr}_{i!s}"
                else:
                    dkey = attr
                alerts[dkey] = getattr(alert, attr)
        self._alerts = alerts

        return len(data)
