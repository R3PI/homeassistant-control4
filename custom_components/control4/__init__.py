"""
Support for Control4 devices

For more details about this component, please refer to the documentation at
https://github.com/r3pi/homeassistant-control4
"""

import logging
import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_URL = 'url'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_URL): cv.url
    })
}, extra=vol.ALLOW_EXTRA)

DATA_CONTROL4 = 'control4'
DATA_CONTROL4_CONFIG = 'control4_config'

REQUIREMENTS = ['python-control4-lite===0.1.0']


async def async_setup(hass, config):
    """Setup Control4 Controller"""

    _LOGGER.debug( 'control4.control4.async_setup', config )

    if DOMAIN not in config:
        return

    conf = config[DOMAIN]
    hass.data[DATA_CONTROL4_CONFIG] = conf
    return True


async def async_setup_entry(hass, entry):
    """Setup Control4 from a config entry"""
    _LOGGER.debug( 'control4.control4.async_setup_entry', entry )

    from control4 import Control4

    control4 = Control4(url=entry.data['url'])

    conf = hass.data.get(DATA_CONTROL4_CONFIG, {})

    hass.data[DATA_CONTROL4] = Control4Device(hass, conf, control4)

    if not await hass.async_add_job(hass.data[DATA_CONTROL4].initialize):
        return False

    # for component in 'light':
    #    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, component))


class Control4Device:
    """Structure Control4 functions for hass."""

    def __init__(self, hass, conf, control4):
        """Init Control4 Devices"""
        self.hass = hass
        self.conf = conf
        self.control4 = control4

    @property
    def control4(self):
        return self.control4

