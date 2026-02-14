"""ESP32 Modes Controller integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

DOMAIN = "esp32_modes"
PLATFORMS = ["select", "button", "sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ESP32 Modes from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    host = entry.data["host"]
    session = async_get_clientsession(hass)
    
    hass.data[DOMAIN][entry.entry_id] = {
        "host": host,
        "session": session,
        "api": ESP32ModesAPI(host, session)
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

class ESP32ModesAPI:
    """API client for ESP32."""
    
    def __init__(self, host, session):
        self.host = host
        self.session = session
        self.base_url = f"http://{host}"
    
    async def get_mode(self):
        """Get current mode."""
        try:
            async with self.session.get(f"{self.base_url}/api/mode", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("mode")
        except Exception as e:
            _LOGGER.error(f"Error getting mode: {e}")
            return None
    
    async def set_mode(self, mode):
        """Set mode (1, 2, or 3)."""
        try:
            async with self.session.get(f"{self.base_url}/api/mode/set{mode}", timeout=5) as response:
                return response.status == 200
        except Exception as e:
            _LOGGER.error(f"Error setting mode: {e}")
            return False
    
    async def reboot(self):
        """Reboot ESP32."""
        try:
            async with self.session.get(f"{self.base_url}/api/reboot", timeout=5) as response:
                return response.status == 200
        except Exception as e:
            _LOGGER.error(f"Error rebooting: {e}")
            return False
