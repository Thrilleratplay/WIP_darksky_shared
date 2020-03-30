from datetime import timedelta

DEFAULT_NAME = "Custom Dark Sky"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=3)
DEFAULT_MODE = "hourly"

ATTRIBUTION = "Powered by Dark Sky"

ALERTS_ATTRS = ["time", "description", "expires", "severity", "uri", "regions", "title"]

CONF_FORECAST = "forecast"
CONF_HOURLY_FORECAST = "hourly_forecast"
CONF_LANGUAGE = "language"
CONF_UNITS = "units"

DOMAIN = "custom_darksky"

DARKSKY_PLATFORMS = ("sensor", "weather")

FORECAST_MODE = ["hourly", "daily"]

DEPRECATED_SENSOR_TYPES = {
    "apparent_temperature_max",
    "apparent_temperature_min",
    "temperature_max",
    "temperature_min",
}

SENSOR_LABELS = {
    "alerts": "Alerts",
    "apparent_temperature_high": "Daytime High Apparent Temperature",
    "apparent_temperature_low": "Overnight Low Apparent Temperature",
    "apparent_temperature_max": "Daily High Apparent Temperature",
    "apparent_temperature_min": "Daily Low Apparent Temperature",
    "apparent_temperature": "Apparent Temperature",
    "cloud_cover": "Cloud Coverage",
    "daily_summary": "Daily Summary",
    "dew_point": "Dew Point",
    "hourly_summary": "Hourly Summary",
    "humidity": "Humidity",
    "icon": "Icon",
    "minutely_summary": "Minutely Summary",
    "moon_phase": "Moon Phase",
    "nearest_storm_bearing": "Nearest Storm Bearing",
    "nearest_storm_distance": "Nearest Storm Distance",
    "ozone": "Ozone",
    "precip_accumulation": "Precip Accumulation",
    "precip_intensity_max": "Daily Max Precip Intensity",
    "precip_intensity": "Precip Intensity",
    "precip_probability": "Precip Probability",
    "precip_type": "Precip",
    "pressure": "Pressure",
    "summary": "Summary",
    "sunrise_time": "Sunrise",
    "sunset_time": "Sunset",
    "temperature_high": "Daytime High Temperature",
    "temperature_low": "Overnight Low Temperature",
    "temperature_max": "Daily High Temperature",
    "temperature_min": "Daily Low Temperature",
    "temperature": "Temperature",
    "uv_index": "UV Index",
    "visibility": "Visibility",
    "wind_bearing": "Wind Bearing",
    "wind_gust": "Wind Gust",
    "wind_speed": "Wind Speed",
}


CURRENTLY_SENSOR = [
    "apparent_temperature",
    "cloud_cover",
    "dew_point",
    "humidity",
    "icon",
    "nearest_storm_bearing",
    "nearest_storm_distance",
    "ozone",
    "precip_intensity",
    "precip_probability",
    "precip_type",
    "pressure",
    "summary",
    "temperature",
    "uv_index",
    "visibility",
    "wind_bearing",
    "wind_gust",
    "wind_speed",
]

DAILY_SENSOR = [
    "apparent_temperature_high",
    "apparent_temperature_low",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "cloud_cover",
    "dew_point",
    "humidity",
    "icon",
    "moon_phase",
    "ozone",
    "precip_accumulation",
    "precip_intensity_max",
    "precip_intensity",
    "precip_probability",
    "precip_type",
    "pressure",
    "summary",
    "sunrise_time",
    "sunset_time",
    "temperature_high",
    "temperature_low",
    "temperature_max",
    "temperature_min",
    "uv_index",
    "visibility",
    "wind_bearing",
    "wind_gust",
    "wind_speed",
]

HOURLY_SENSOR = [
    "apparent_temperature",
    "cloud_cover",
    "dew_point",
    "humidity",
    "icon",
    "ozone",
    "precip_accumulation",
    "precip_intensity",
    "precip_probability",
    "precip_type",
    "pressure",
    "summary",
    "temperature",
    "uv_index",
    "visibility",
    "wind_bearing",
    "wind_gust",
    "wind_speed",
]

MINUTELY_SENSOR = [
    "precip_intensity",
    "precip_probability",
    "precip_type",
]


CONDITION_PICTURES = {
    "clear-day": "/static/images/darksky/weather-sunny.svg",
    "clear-night": "/static/images/darksky/weather-night.svg",
    "cloudy": "/static/images/darksky/weather-cloudy.svg",
    "fog": "/static/images/darksky/weather-fog.svg",
    "partly-cloudy-day": "/static/images/darksky/weather-partlycloudy.svg",
    "partly-cloudy-night": "/static/images/darksky/weather-cloudy.svg",
    "rain": "/static/images/darksky/weather-pouring.svg",
    "sleet": "/static/images/darksky/weather-hail.svg",
    "snow": "/static/images/darksky/weather-snowy.svg",
    "wind": "/static/images/darksky/weather-windy.svg",
}

ICONS = {
    "alerts": "mdi:alert-circle-outline",
    "apparent_temperature_high": "mdi:thermometer",
    "apparent_temperature_low": "mdi:thermometer",
    "apparent_temperature_max": "mdi:thermometer",
    "apparent_temperature_min": "mdi:thermometer",
    "apparent_temperature": "mdi:thermometer",
    "clear-day": "mdi:weather-sunny",
    "clear-night": "mdi:weather-night",
    "cloud_cover": "mdi:weather-partly-cloudy",
    "cloudy": "mdi:weather-cloudy",
    "dew_point": "mdi:thermometer",
    "fog": "mdi:weather-fog",
    "humidity": "mdi:water-percent",
    "moon_phase": "mdi:weather-night",
    "nearest_storm_bearing": "mdi:weather-lightning",
    "nearest_storm_distance": "mdi:weather-lightning",
    "ozone": "mdi:eye",
    "partly-cloudy-day": "mdi:weather-partly-cloudy",
    "partly-cloudy-night": "mdi:weather-night-partly-cloudy",
    "precip_accumulation": "mdi:weather-snowy",
    "precip_intensity_max": "mdi:thermometer",
    "precip_intensity": "mdi:weather-rainy",
    "precip_probability": "mdi:water-percent",
    "precip_type": "mdi:weather-pouring",
    "pressure": "mdi:gauge",
    "rain": "mdi:weather-pouring",
    "sleet": "mdi:weather-snowy-rainy",
    "snow": "mdi:weather-snowy",
    "sunrise_time": "mdi:white-balance-sunny",
    "sunset_time": "mdi:weather-night",
    "temperature_high": "mdi:thermometer",
    "temperature_low": "mdi:thermometer",
    "temperature_max": "mdi:thermometer",
    "temperature_min": "mdi:thermometer",
    "temperature": "mdi:thermometer",
    "uv_index": "mdi:weather-sunny",
    "visibility": "mdi:eye",
    "wind_bearing": "mdi:compass",
    "wind_gust": "mdi:weather-windy-variant",
    "wind_speed": "mdi:weather-windy",
    "wind": "mdi:weather-windy",
}

MAP_CONDITION = {
    "clear-day": "sunny",
    "clear-night": "clear-night",
    "rain": "rainy",
    "snow": "snowy",
    "sleet": "snowy-rainy",
    "wind": "windy",
    "fog": "fog",
    "cloudy": "cloudy",
    "partly-cloudy-day": "partlycloudy",
    "partly-cloudy-night": "partlycloudy",
    "hail": "hail",
    "thunderstorm": "lightning",
    "tornado": None,
}
