from homeassistant.util.pressure import convert as convert_pressure
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

from .const import (
    DEFAULT_NAME,
    DEFAULT_MODE,
    DOMAIN,
    FORECAST_MODE,
    ATTRIBUTION,
    MAP_CONDITION,
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


def xstr(s):
    """
    Return string or empty string if None.

    https://stackoverflow.com/a/1034598
    """
    return "" if s is None else str(s)


def unit_of_measurement(sensor_type, unit_type):
    """Return unit of a given measurement for unit type."""
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


def imperial_pressure(pressure):
    """Convert pressure to imperial/US."""
    return round(convert_pressure(pressure, PRESSURE_HPA, PRESSURE_INHG), 2)


def calc_precipitation(intensity, hours):
    """Calculate precipiation accumulation."""
    amount = None
    if intensity is not None:
        amount = round((intensity * hours), 1)
    return amount if amount > 0 else None


def format_daily_forecast(data):
    """Format forecast per day."""
    return [
        {
            ATTR_FORECAST_TIME: entry.time.isoformat(),
            ATTR_FORECAST_TEMP: entry.temperature_high,
            ATTR_FORECAST_TEMP_LOW: entry.temperature_low,
            ATTR_FORECAST_PRECIPITATION: calc_precipitation(entry.precip_intensity, 24),
            ATTR_FORECAST_WIND_SPEED: entry.wind_speed,
            ATTR_FORECAST_WIND_BEARING: entry.wind_bearing,
            ATTR_FORECAST_CONDITION: MAP_CONDITION.get(entry.icon),
        }
        for entry in data
    ]


def format_hourly_forecast(data):
    """Format forecast per hour."""
    return [
        {
            ATTR_FORECAST_TIME: entry.time.isoformat(),
            ATTR_FORECAST_TEMP: entry.temperature,
            ATTR_FORECAST_PRECIPITATION: calc_precipitation(entry.precip_intensity, 1),
            ATTR_FORECAST_CONDITION: MAP_CONDITION.get(entry.icon),
        }
        for entry in data
    ]
