"""Sensor platform for ESP32 Modes."""
import logging
from homeassistant.components.sensor import SensorEntity
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
    """Set up the sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ESP32ModeSensor(data["api"], entry.entry_id)])

class ESP32ModeSensor(SensorEntity):
    """Representation of ESP32 Mode sensor."""
    
    _attr_has_entity_name = True
    _attr_translation_key = "mode_sensor"
    _attr_should_poll = True
    
    def __init__(self, api, entry_id):
        """Initialize the sensor."""
        self._api = api
        self._attr_unique_id = f"{entry_id}_mode_sensor"
        self._attr_name = "Mode Actuel"
        self._state = None
        self._attr_scan_interval = 5
    
    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state
    
    async def async_update(self):
        """Fetch new state data."""
        mode = await self._api.get_mode()
        if mode:
            self._state = f"Mode {mode}"
