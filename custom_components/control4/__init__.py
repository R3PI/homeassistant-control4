"""
Support for Control4 devices

For more details about this component, please refer to the documentation at
https://github.com/r3pi/homeassistant-control4
"""

import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from .const import ( DOMAIN )

CONF_HOST = 'host'
CONF_PORT = 'port'
CONF_PROTOCOL = 'protocol'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Optional(CONF_PROTOCOL, default='http'): cv.string
    })
}, extra=vol.ALLOW_EXTRA)

DATA_CONTROL4 = 'control4'
DATA_CONTROL4_CONFIG = 'control4_config'

REQUIREMENTS = ['python-control4===0.1.0']


async def async_setup(hass, config):
    """Setup Control4 Controller"""
    if DOMAIN not in config:
        return

    conf = config[DOMAIN]

    hass.data[DATA_CONTROL4_CONFIG] = config

    return True


async def async_setup_entry(hass, entry):
    """Setup Control4 from a config entry"""
    from control4 import Control4

    control4 = Control4(host=entry.data['host'], port=entry.data['port'], protocol=entry.data['protocol'])

    conf = hass.data.get(DATA_CONTROL4_CONFIG, {})

    hass.data[DATA_CONTROL4] = Control4Device(hass, conf, control4)

    if not await hass.async_add_job(hass.data[DATA_CONTROL4].initialize):
        return False

    for component in 'climate', 'camera', 'sensor', 'binary_sensor':
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, component))



class Control4Device:
    """Structure Control4 functions for hass."""

    def __init__(self, hass, conf, control4):
        """Init Control4 Devices"""
        self.hass = hass
        self.control4 = control4


    def initialize(self):
        """Initialize Control4"""
        return True

