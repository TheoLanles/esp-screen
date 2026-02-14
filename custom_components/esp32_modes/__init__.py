"""ESP32 Modes Controller integration."""
import logging
import os
import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "esp32_modes"
PLATFORMS = ["select", "button", "sensor"]

SERVICE_UPDATE_FIRMWARE = "update_firmware"
ATTR_FIRMWARE_PATH = "firmware_path"
ATTR_ENTRY_ID = "entry_id"

SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_FIRMWARE_PATH): cv.string,
    vol.Optional(ATTR_ENTRY_ID): cv.string,
})

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
    
    # Register service only once
    if not hass.services.has_service(DOMAIN, SERVICE_UPDATE_FIRMWARE):
        async def handle_update_firmware(call: ServiceCall) -> None:
            """Handle the update_firmware service call."""
            firmware_path = call.data[ATTR_FIRMWARE_PATH]
            entry_id = call.data.get(ATTR_ENTRY_ID)
            
            if not os.path.isfile(firmware_path):
                _LOGGER.error("Firmware file not found: %s", firmware_path)
                raise ValueError(f"Firmware file not found: {firmware_path}")
            
            if not firmware_path.endswith(".bin"):
                _LOGGER.error("Invalid firmware file (must be .bin): %s", firmware_path)
                raise ValueError("Firmware file must be a .bin file")
            
            # Find the target ESP32
            if entry_id:
                if entry_id not in hass.data[DOMAIN]:
                    raise ValueError(f"Unknown entry_id: {entry_id}")
                api = hass.data[DOMAIN][entry_id]["api"]
            else:
                # Use the first (or only) configured ESP32
                first_entry = next(iter(hass.data[DOMAIN].values()))
                api = first_entry["api"]
            
            _LOGGER.info("Starting OTA update with file: %s", firmware_path)
            success = await api.upload_firmware(firmware_path)
            
            if success:
                _LOGGER.info("OTA update successful, ESP32 is rebooting")
            else:
                _LOGGER.error("OTA update failed")
                raise RuntimeError("OTA update failed")
        
        hass.services.async_register(
            DOMAIN, SERVICE_UPDATE_FIRMWARE, handle_update_firmware, schema=SERVICE_SCHEMA
        )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    # Remove service if no more entries
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_UPDATE_FIRMWARE)
    
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
            _LOGGER.error("Error getting mode: %s", e)
            return None
    
    async def set_mode(self, mode):
        """Set mode (1, 2, or 3)."""
        try:
            async with self.session.get(f"{self.base_url}/api/mode/set{mode}", timeout=5) as response:
                return response.status == 200
        except Exception as e:
            _LOGGER.error("Error setting mode: %s", e)
            return False
    
    async def reboot(self):
        """Reboot ESP32."""
        try:
            async with self.session.get(f"{self.base_url}/api/reboot", timeout=5) as response:
                return response.status == 200
        except Exception as e:
            _LOGGER.error("Error rebooting: %s", e)
            return False
    
    async def upload_firmware(self, firmware_path):
        """Upload firmware .bin file to ESP32 via OTA."""
        try:
            with open(firmware_path, "rb") as f:
                firmware_data = f.read()
            
            form = aiohttp.FormData()
            form.add_field(
                "firmware",
                firmware_data,
                filename=os.path.basename(firmware_path),
                content_type="application/octet-stream"
            )
            
            _LOGGER.info(
                "Uploading firmware (%d bytes) to %s",
                len(firmware_data), self.base_url
            )
            
            async with self.session.post(
                f"{self.base_url}/api/update",
                data=form,
                timeout=120
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    _LOGGER.info("OTA result: %s", result)
                    return True
                else:
                    _LOGGER.error("OTA failed with status %d", response.status)
                    return False
        except Exception as e:
            _LOGGER.error("Error uploading firmware: %s", e)
            return False
