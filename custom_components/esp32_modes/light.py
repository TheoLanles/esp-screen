"""Light platform for ESP32 NeoPixel Screen."""
import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)
DOMAIN = "esp32_modes"

EFFECT_SOLID = "solid"
EFFECT_RAINBOW = "rainbow"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NeoPixelLight(data["api"], entry.entry_id)])


class NeoPixelLight(LightEntity):
    """NeoPixel 8×64 screen as a HA light."""

    _attr_has_entity_name = True
    _attr_name = "Écran NeoPixel"
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = [EFFECT_SOLID, EFFECT_RAINBOW]
    _attr_should_poll = True

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_light"
        self._is_on = True
        self._brightness = 60
        self._rgb = (255, 80, 0)
        self._effect = EFFECT_SOLID

    @property
    def is_on(self) -> bool:
        return self._is_on

    @property
    def brightness(self) -> int:
        return self._brightness

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        return self._rgb

    @property
    def effect(self) -> str:
        return self._effect

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on / update settings."""
        if not self._is_on:
            await self._api.set_power(True)
            self._is_on = True

        if ATTR_RGB_COLOR in kwargs:
            r, g, b = kwargs[ATTR_RGB_COLOR]
            await self._api.set_color(r, g, b)
            self._rgb = (r, g, b)

        if ATTR_BRIGHTNESS in kwargs:
            bri = kwargs[ATTR_BRIGHTNESS]
            await self._api.set_brightness(bri)
            self._brightness = bri

        if ATTR_EFFECT in kwargs:
            effect = kwargs[ATTR_EFFECT]
            await self._api.set_mode(effect)
            self._effect = effect

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self._api.set_power(False)
        self._is_on = False
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Poll status from ESP32."""
        status = await self._api.get_status()
        if status is None:
            return
        self._is_on = status.get("power") == "ON"
        self._brightness = status.get("brightness", 60)
        c = status.get("color", {})
        self._rgb = (c.get("r", 255), c.get("g", 80), c.get("b", 0))
        mode = status.get("mode", "solid")
        self._effect = EFFECT_RAINBOW if mode == "rainbow" else EFFECT_SOLID
