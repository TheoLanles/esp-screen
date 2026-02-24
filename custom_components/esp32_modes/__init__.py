"""ESP32 NeoPixel Screen integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

DOMAIN = "esp32_modes"
PLATFORMS = ["light", "text", "number", "switch", "sensor", "button"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ESP32 NeoPixel Screen from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data["host"]
    session = async_get_clientsession(hass)
    api = ESP32ScreenAPI(host, session)

    hass.data[DOMAIN][entry.entry_id] = {
        "host": host,
        "session": session,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class ESP32ScreenAPI:
    """HTTP API client for the ESP32 NeoPixel Screen."""

    def __init__(self, host: str, session) -> None:
        self.host = host
        self.session = session
        self.base_url = f"http://{host}"
        self._state: dict | None = None

    async def get_status(self) -> dict | None:
        """GET /api/status → full state JSON."""
        try:
            async with self.session.get(
                f"{self.base_url}/api/status", timeout=5
            ) as resp:
                if resp.status == 200:
                    self._state = await resp.json()
                    return self._state
        except Exception as exc:
            _LOGGER.error("Error getting status: %s", exc)
        return None

    async def set_text(self, text: str) -> bool:
        return await self._get(f"/api/text/set?value={text}")

    async def set_color(self, r: int, g: int, b: int) -> bool:
        return await self._get(f"/api/color/set?r={r}&g={g}&b={b}")

    async def set_brightness(self, value: int) -> bool:
        return await self._get(f"/api/brightness/set?value={value}")

    async def set_speed(self, value: int) -> bool:
        return await self._get(f"/api/speed/set?value={value}")

    async def set_mode(self, mode: str) -> bool:
        return await self._get(f"/api/mode/set?value={mode}")

    async def set_scroll(self, on: bool) -> bool:
        return await self._get(f"/api/scroll/set?value={'ON' if on else 'OFF'}")

    async def set_power(self, on: bool) -> bool:
        return await self._get(f"/api/power/set?value={'ON' if on else 'OFF'}")

    async def set_matrix(self, w: int, h: int) -> bool:
        return await self._get(f"/api/matrix/set?w={w}&h={h}")

    async def reboot(self) -> bool:
        return await self._get("/api/reboot")

    async def get_temp(self) -> float | None:
        """GET /api/temp → {"temp": ...}."""
        try:
            async with self.session.get(
                f"{self.base_url}/api/temp", timeout=5
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("temp")
        except Exception as exc:
            _LOGGER.error("Error getting temp: %s", exc)
        return None

    # ── internal helper ──────────────────────────────────────
    async def _get(self, path: str) -> bool:
        try:
            async with self.session.get(
                f"{self.base_url}{path}", timeout=5
            ) as resp:
                if resp.status == 200:
                    self._state = await resp.json()
                    return True
        except Exception as exc:
            _LOGGER.error("API call failed (%s): %s", path, exc)
        return False
