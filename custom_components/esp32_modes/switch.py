"""Switch platform for ESP32 NeoPixel Screen."""
import logging
from homeassistant.components.switch import SwitchEntity
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
    async_add_entities([NeoPixelScroll(data["api"], entry.entry_id)])


class NeoPixelScroll(SwitchEntity):
    """Toggle scrolling ON/OFF."""

    _attr_has_entity_name = True
    _attr_name = "Défilement"
    _attr_icon = "mdi:autorenew"
    _attr_should_poll = True

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_scroll"
        self._attr_is_on = True

    async def async_turn_on(self, **kwargs) -> None:
        await self._api.set_scroll(True)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        await self._api.set_scroll(False)
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_update(self) -> None:
        status = await self._api.get_status()
        if status:
            self._attr_is_on = status.get("scrolling") == "ON"
