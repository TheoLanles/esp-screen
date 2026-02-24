"""Sensor platform for ESP32 NeoPixel Screen."""
import logging
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)
DOMAIN = "esp32_modes"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        NeoPixelRAMSensor(data["api"], entry.entry_id),
        NeoPixelTempSensor(data["api"], entry.entry_id),
    ])


class NeoPixelRAMSensor(SensorEntity):
    """Free heap RAM sensor."""

    _attr_has_entity_name = True
    _attr_name = "RAM libre"
    _attr_icon = "mdi:memory"
    _attr_native_unit_of_measurement = "B"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_should_poll = True

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_ram"
        self._attr_native_value = None

    async def async_update(self) -> None:
        status = await self._api.get_status()
        if status:
            self._attr_native_value = status.get("heap_free")


class NeoPixelTempSensor(SensorEntity):
    """Internal temperature sensor."""

    _attr_has_entity_name = True
    _attr_name = "Température Interne"
    _attr_icon = "mdi:thermometer"
    _attr_native_unit_of_measurement = "°C"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = "temperature"
    _attr_should_poll = True

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_temp"
        self._attr_native_value = None

    async def async_update(self) -> None:
        val = await self._api.get_temp()
        if val is not None:
            self._attr_native_value = val
