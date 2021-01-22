from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import PERCENTAGE

import logging

from screenlogicpy.const import ON_OFF

from . import ScreenlogicEntity

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    PUMP_BREAKOUT_SENSORS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up entry."""
    entities = []
    coordinator = hass.data[DOMAIN][config_entry.unique_id]["coordinator"]
    # Generic sensors
    for sensor in hass.data[DOMAIN][config_entry.unique_id]["devices"]["sensor"]:
        _LOGGER.debug(sensor)
        entities.append(ScreenLogicSensor(coordinator, sensor))
    for pump in hass.data[DOMAIN][config_entry.unique_id]["devices"]["pump"]:
        for breakoutSensor in PUMP_BREAKOUT_SENSORS:
            if breakoutSensor in coordinator.data["pumps"][pump]:
                entities.append(
                    ScreenLogicPumpSensor(coordinator, pump, breakoutSensor)
                )

    async_add_entities(entities, True)


class ScreenLogicSensor(ScreenlogicEntity):
    """Representation of a ScreenLogic sensor entity"""

    def __init__(self, coordinator, sensor):
        """Initialize of the sensor."""
        super().__init__(coordinator, sensor)

    @property
    def name(self):
        """Return the sensor name"""
        return (
            "ScreenLogic " + self.coordinator.data["sensors"][self._entity_id]["name"]
        )

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement"""
        if "unit" in self.coordinator.data["sensors"][self._entity_id]:
            return self.coordinator.data["sensors"][self._entity_id]["unit"]
        else:
            return None

    @property
    def device_class(self):
        """Return the device class."""
        if "hass_device_class" in self.coordinator.data["sensors"][self._entity_id]:
            return self.coordinator.data["sensors"][self._entity_id][
                "hass_device_class"
            ]
        else:
            return None

    @property
    def state(self):
        """ Retruns the state of the sensor """
        value = self.coordinator.data["sensors"][self._entity_id]["value"]
        return (value - 1) if "supply" in self._entity_id else value


class ScreenLogicPumpSensor(ScreenlogicEntity):
    """Representation of a ScreenLogic pump sensor entity"""

    def __init__(self, coordinator, pump, key):
        """Initialize of the pump sensor."""
        ent_id = str(key) + "_" + str(pump)
        super().__init__(coordinator, ent_id)
        self._pump_id = pump
        self._key = key

    @property
    def name(self):
        """Return the pump sensor name"""
        return (
            "ScreenLogic "
            + self.coordinator.data["pumps"][self._pump_id][self._key]["name"]
        )

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement"""
        if "unit" in self.coordinator.data["pumps"][self._pump_id][self._key]:
            return self.coordinator.data["pumps"][self._pump_id][self._key]["unit"]
        else:
            return None

    @property
    def device_class(self):
        """Return the device class."""
        if (
            "hass_device_class"
            in self.coordinator.data["pumps"][self._pump_id][self._key]
        ):
            return self.coordinator.data["pumps"][self._pump_id][self._key][
                "hass_device_class"
            ]
        else:
            return None

    @property
    def state(self):
        """ Retruns the state of the pump sensor """
        return self.coordinator.data["pumps"][self._pump_id][self._key]["value"]
