"""Button platform for ESP32 NeoPixel Screen."""
import logging
from homeassistant.components.button import ButtonEntity
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
    async_add_entities([ESP32RebootButton(data["api"], entry.entry_id)])


class ESP32RebootButton(ButtonEntity):
    """Reboot button."""

    _attr_has_entity_name = True
    _attr_name = "Redémarrer"
    _attr_icon = "mdi:restart"
    _attr_translation_key = "reboot"

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_reboot"

    async def async_press(self) -> None:
        await self._api.reboot()
        _LOGGER.info("ESP32 reboot requested")
