"""Select platform for ESP32 Modes."""
import logging
from homeassistant.components.select import SelectEntity
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
    """Set up the select platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ESP32ModeSelect(data["api"], entry.entry_id)])

class ESP32ModeSelect(SelectEntity):
    """Representation of ESP32 Mode selector."""
    
    _attr_options = ["Mode 1", "Mode 2", "Mode 3"]
    _attr_has_entity_name = True
    _attr_translation_key = "mode"
    _attr_should_poll = True
    
    def __init__(self, api, entry_id):
        """Initialize the select."""
        self._api = api
        self._attr_unique_id = f"{entry_id}_mode"
        self._attr_name = "Mode"
        self._current_option = "Mode 1"
        self._attr_scan_interval = 5
    
    @property
    def current_option(self):
        """Return the selected option."""
        return self._current_option
    
    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        mode_map = {"Mode 1": 1, "Mode 2": 2, "Mode 3": 3}
        mode = mode_map.get(option)
        
        if mode and await self._api.set_mode(mode):
            self._current_option = option
            self.async_write_ha_state()
    
    async def async_update(self):
        """Fetch new state data."""
        mode = await self._api.get_mode()
        if mode:
            mode_reverse_map = {1: "Mode 1", 2: "Mode 2", 3: "Mode 3"}
            self._current_option = mode_reverse_map.get(mode, "Mode 1")
