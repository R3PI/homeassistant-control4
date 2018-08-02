"""
Support for Control4 lights.
For more details about this platform, please refer to the documentation at
https://github.com/r3pi/homeassistant-control4/custom_components/light/
"""
import logging
from functools import wraps
import time

import voluptuous as vol

from homeassistant.const import (
    CONF_LATITUDE, CONF_LONGITUDE, CONF_DEVICES, CONF_NAME, CONF_SCAN_INTERVAL
)

from homeassistant.components.light import (
    ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, Light, PLATFORM_SCHEMA
)

from homeassistant.helpers import config_validation as cv

DATA_CONTROL4 = 'control4'


_LOGGER = logging.getLogger(__name__)
DEPENDENCIES = ['control4']

CONF_DESC = 'desc'
CONF_C4ID = 'c4id'
CONF_DIMMABLE = 'dimmable'
CONF_C4VAR_BRIGHTNESS = 'c4var_brightness'
CONF_C4VAR_STATUS = 'c4var_status'

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_C4ID): cv.positive_int,
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(CONF_DESC, default=""): cv.string,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_DIMMABLE, default=True): cv.boolean,
    vol.Optional(CONF_C4VAR_BRIGHTNESS, default=1001): cv.positive_int,
    vol.Optional(CONF_C4VAR_STATUS, default=1000): cv.positive_int,
    vol.Optional(CONF_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=1))
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_DEVICES, default={}): {cv.string: DEVICE_SCHEMA}
})


def retry(method):
    """Retry Control4 commands."""
    @wraps(method)
    def wrapper_retry(device, *args, **kwargs):
        """Try send command and retry on error"""
        initial = time.monotonic()

        while True:
            if time.monotonic() - initial >= 10:
                return None
            try:
                return method(device, *args, **kwargs)
            except Exception as e:
                _LOGGER.warning("Control4 connect error for device %s: %s", device.name, str(e))
    return wrapper_retry


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up Control4 lights"""
    light = Control4Light(entry, hass.data[DATA_CONTROL4].control4)

    async_add_devices([light], True)


class Control4Light(Light):
    """Representation of a Control4 Light"""

    def __init__(self, device, switch):
        """Initialize the light"""
        self._name = device['name']
        self._c4id = device['c4id']
        self._desc = device['desc']
        self._latitude = device['latitude']
        self._longitude = device['longitude']
        self._dimmable = device['dimmable']
        self._c4var_brightness = device['c4var_brightness']
        self._c4var_status = device['c4var_status']

        self._switch = switch
        self._state = False
        self._brightness = 0

    @property
    def unique_id(self):
        """Return the ID of this light."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def supported_features(self):
        """Flag supported features."""
        if self._dimmable:
            return SUPPORT_BRIGHTNESS
        return 0

    @property
    def assumed_state(self):
        """We can read the actual state."""
        return False

    @retry
    def set_state(self, brightness):
        """"Set the state of this light to the provided brightness."""
        self._switch.set('SET_LEVEL', {'LEVEL': brightness(int(brightness / 2.55))})

    @retry
    def turn_on(self, **kwargs):
        """Turn the light on"""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        self._switch.set('ON')
        self._state = True

        if brightness is not None:
            self.set_state(brightness)

    @retry
    def turn_off(self, **kwargs):
        """Turn the light off"""
        self._switch.set('OFF')
        self._state = False

    @retry
    def update(self):
        """Synchronize internal state with the actual light state."""
        if self._dimmable:
            self._brightness = float(self._switch.get(self._c4var_brightness)) * 2.55

        self._state = bool(self._switch.get(self._c4var_status))
