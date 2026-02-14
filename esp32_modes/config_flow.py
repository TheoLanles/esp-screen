"""Config flow for ESP32 Modes."""
import voluptuous as vol
import aiohttp
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

DOMAIN = "esp32_modes"

class ESP32ModesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            host = user_input[CONF_HOST]
            
            # Tester la connexion à l'API
            session = async_get_clientsession(self.hass)
            try:
                async with session.get(f"http://{host}/api/mode", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "mode" in data:
                            # Connexion réussie
                            await self.async_set_unique_id(host)
                            self._abort_if_unique_id_configured()
                            
                            return self.async_create_entry(
                                title=f"ESP32 Modes ({host})",
                                data=user_input
                            )
                    errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default="192.168.1.100"): str,
            }),
            errors=errors,
            description_placeholders={
                "example": "192.168.1.100"
            }
        )
