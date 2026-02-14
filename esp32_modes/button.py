"""Button platform for ESP32 Modes."""
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
    """Set up the button platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ESP32RebootButton(data["api"], entry.entry_id)])

class ESP32RebootButton(ButtonEntity):
    """Representation of ESP32 Reboot button."""
    
    _attr_has_entity_name = True
    _attr_translation_key = "reboot"
    
    def __init__(self, api, entry_id):
        """Initialize the button."""
        self._api = api
        self._attr_unique_id = f"{entry_id}_reboot"
        self._attr_name = "Reboot"
    
    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api.reboot()
        _LOGGER.info("ESP32 reboot requested")
