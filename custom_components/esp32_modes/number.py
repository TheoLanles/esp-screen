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
    api = data["api"]
    eid = entry.entry_id
    async_add_entities([
        NeoPixelSpeed(api, eid),
        NeoPixelMatrixW(api, eid),
        NeoPixelMatrixH(api, eid),
    ])


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


class NeoPixelMatrixW(NumberEntity):
    """Matrix width (number of columns)."""

    _attr_has_entity_name = True
    _attr_name = "Largeur matrice"
    _attr_icon = "mdi:arrow-left-right"
    _attr_native_min_value = 1
    _attr_native_max_value = 256
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "px"
    _attr_mode = NumberMode.BOX
    _attr_should_poll = True

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_matrix_w"
        self._attr_native_value = 64
        self._matrix_h = 8  # cache for set_matrix call

    async def async_set_native_value(self, value: float) -> None:
        w = int(value)
        if w * self._matrix_h > 1024:
            _LOGGER.warning("w*h exceeds 1024 pixels, ignoring")
            return
        await self._api.set_matrix(w, self._matrix_h)
        self._attr_native_value = w
        self.async_write_ha_state()

    async def async_update(self) -> None:
        status = await self._api.get_status()
        if status:
            m = status.get("matrix", {})
            self._attr_native_value = m.get("w", 64)
            self._matrix_h = m.get("h", 8)


class NeoPixelMatrixH(NumberEntity):
    """Matrix height (number of rows)."""

    _attr_has_entity_name = True
    _attr_name = "Hauteur matrice"
    _attr_icon = "mdi:arrow-up-down"
    _attr_native_min_value = 1
    _attr_native_max_value = 64
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "px"
    _attr_mode = NumberMode.BOX
    _attr_should_poll = True

    def __init__(self, api, entry_id: str) -> None:
        self._api = api
        self._attr_unique_id = f"{entry_id}_matrix_h"
        self._attr_native_value = 8
        self._matrix_w = 64  # cache for set_matrix call

    async def async_set_native_value(self, value: float) -> None:
        h = int(value)
        if self._matrix_w * h > 1024:
            _LOGGER.warning("w*h exceeds 1024 pixels, ignoring")
            return
        await self._api.set_matrix(self._matrix_w, h)
        self._attr_native_value = h
        self.async_write_ha_state()

    async def async_update(self) -> None:
        status = await self._api.get_status()
        if status:
            m = status.get("matrix", {})
            self._attr_native_value = m.get("h", 8)
            self._matrix_w = m.get("w", 64)
