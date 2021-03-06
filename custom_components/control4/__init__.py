"""
Support for Control4 devices

For more details about this component, please refer to the documentation at
https://github.com/r3pi/homeassistant-control4
"""

import logging
import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_URL = 'url'
CONF_PROXY = 'proxy'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_URL): cv.url,
        vol.Optional(CONF_PROXY, default=None): cv.url
    })
}, extra=vol.ALLOW_EXTRA)

DATA_CONTROL4 = 'control4'
DATA_CONTROL4_CONFIG = 'control4_config'

REQUIREMENTS = ['python-control4-lite===0.1.15']


async def async_setup(hass, config):
    """Setup Control4 Controller"""

    _LOGGER.debug('async_setup: %s', str(config))

    if DOMAIN not in config:
        return

    _LOGGER.debug('async_setup has config')

    from control4 import Control4

    conf = config[DOMAIN]

    # May need to avoid aviod 'session=async_get_clientsession(hass)' here,
    # because Control4 seems to require force_close -- TBD
    control4 = Control4(url=conf['url'], session=async_get_clientsession(hass), proxy=conf['proxy'])

    hass.data[DATA_CONTROL4_CONFIG] = conf
    hass.data[DATA_CONTROL4] = Control4Device(hass, conf, control4)

    return True

class Control4Device:
    """Structure Control4 functions for hass."""

    def __init__(self, hass, conf, control4):
        """Init Control4 Devices"""
        self._hass = hass
        self._conf = conf
        self._control4 = control4

    @property
    def control4(self):
        return self._control4
