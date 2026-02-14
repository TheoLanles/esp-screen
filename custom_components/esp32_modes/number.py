"""Number platform for ESP32 NeoPixel Screen."""
import logging
from homeassistant.components.number import NumberEntity, NumberMode
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
    async_add_entities([NeoPixelSpeed(data["api"], entry.entry_id)])


class NeoPixelSpeed(NumberEntity):
    """Scroll speed slider (ms between frames)."""

    _attr_has_entity_name = True
    _attr_name = "Vitesse défilement"
    _attr_icon = "mdi:speedometer"
    _attr_native_min_value = 5
    _attr_native_max_value = 500
    _attr_native_step = 5
    _attr_native_unit_of_measurement = "ms"
    _attr_mode = NumberMode.SLIDER
    _attr_should_poll = True

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_speed"
        self._attr_native_value = 40

    async def async_set_native_value(self, value: float) -> None:
        await self._api.set_speed(int(value))
        self._attr_native_value = value
        self.async_write_ha_state()

    async def async_update(self) -> None:
        status = await self._api.get_status()
        if status:
            self._attr_native_value = status.get("speed", 40)
