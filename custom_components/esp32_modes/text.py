"""Text platform for ESP32 NeoPixel Screen."""
import logging
from homeassistant.components.text import TextEntity
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
    async_add_entities([NeoPixelText(data["api"], entry.entry_id)])


class NeoPixelText(TextEntity):
    """Scrolling text input for the NeoPixel screen."""

    _attr_has_entity_name = True
    _attr_name = "Texte défilant"
    _attr_native_max = 127
    _attr_native_min = 1
    _attr_should_poll = True

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_text"
        self._attr_native_value = ""

    async def async_set_value(self, value: str) -> None:
        """Set scrolling text."""
        await self._api.set_text(value)
        self._attr_native_value = value
        self.async_write_ha_state()

    async def async_update(self) -> None:
        status = await self._api.get_status()
        if status:
            self._attr_native_value = status.get("text", "")
