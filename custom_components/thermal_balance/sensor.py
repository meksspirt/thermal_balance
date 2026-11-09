"""Sensor platform for Thermal Balance custom component."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    SENSOR_AC_CARNOT_COP,
    SENSOR_AC_CONDENSATION_RATE,
    SENSOR_AC_ENERGY_COST,
    SENSOR_AC_HEAT_OUTPUT,
    SENSOR_AC_THERMAL_ENERGY_TOTAL,
    SENSOR_DAILY_THERMAL_BALANCE,
    SENSOR_EMPIRICAL_K_FACTOR,
    SENSOR_EQUILIBRIUM_TEMPERATURE,
    SENSOR_INSTANT_HEAT_GAIN,
    SENSOR_INSTANT_NET_BALANCE,
    SENSOR_NET_THERMAL_BALANCE,
    SENSOR_REQUIRED_AC_POWER,
    SENSOR_SHADING_DAILY_SAVINGS,
    SENSOR_TIME_TO_1DEG,
    SENSOR_TOTAL_HEAT_ABSORBED,
)
from .coordinator import ThermalBalanceCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES: Final = 0


@dataclass(frozen=True)
class ThermalBalanceSensorEntityDescription(SensorEntityDescription):
    """Class describing Thermal Balance sensor entities."""

    is_restorable: bool = False


SENSOR_TYPES: tuple[ThermalBalanceSensorEntityDescription, ...] = (
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_INSTANT_HEAT_GAIN,
        translation_key=SENSOR_INSTANT_HEAT_GAIN,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_AC_HEAT_OUTPUT,
        translation_key=SENSOR_AC_HEAT_OUTPUT,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_INSTANT_NET_BALANCE,
        translation_key=SENSOR_INSTANT_NET_BALANCE,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_AC_CARNOT_COP,
        translation_key=SENSOR_AC_CARNOT_COP,
        native_unit_of_measurement=None,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_TIME_TO_1DEG,
        translation_key=SENSOR_TIME_TO_1DEG,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_DAILY_THERMAL_BALANCE,
        translation_key=SENSOR_DAILY_THERMAL_BALANCE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        is_restorable=True,
        suggested_display_precision=3,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_NET_THERMAL_BALANCE,
        translation_key=SENSOR_NET_THERMAL_BALANCE,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        is_restorable=True,
        suggested_display_precision=3,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_TOTAL_HEAT_ABSORBED,
        translation_key=SENSOR_TOTAL_HEAT_ABSORBED,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        is_restorable=True,
        suggested_display_precision=3,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_AC_THERMAL_ENERGY_TOTAL,
        translation_key=SENSOR_AC_THERMAL_ENERGY_TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        is_restorable=True,
        suggested_display_precision=3,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_AC_CONDENSATION_RATE,
        translation_key=SENSOR_AC_CONDENSATION_RATE,
        native_unit_of_measurement="L/h",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_EMPIRICAL_K_FACTOR,
        translation_key=SENSOR_EMPIRICAL_K_FACTOR,
        native_unit_of_measurement="W/K",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_restorable=True,
        suggested_display_precision=2,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_EQUILIBRIUM_TEMPERATURE,
        translation_key=SENSOR_EQUILIBRIUM_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_REQUIRED_AC_POWER,
        translation_key=SENSOR_REQUIRED_AC_POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_AC_ENERGY_COST,
        translation_key=SENSOR_AC_ENERGY_COST,
        native_unit_of_measurement=None,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        is_restorable=True,
        suggested_display_precision=2,
    ),
    ThermalBalanceSensorEntityDescription(
        key=SENSOR_SHADING_DAILY_SAVINGS,
        translation_key=SENSOR_SHADING_DAILY_SAVINGS,
        native_unit_of_measurement=None,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        is_restorable=True,
        suggested_display_precision=2,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Thermal Balance sensors from a config entry."""
    coordinator: ThermalBalanceCoordinator = entry.runtime_data

    async_add_entities(
        ThermalBalanceSensor(coordinator, entry, description)
        for description in SENSOR_TYPES
    )


class ThermalBalanceSensor(CoordinatorEntity[ThermalBalanceCoordinator], RestoreEntity, SensorEntity):
    """Representation of a Thermal Balance Sensor."""

    entity_description: ThermalBalanceSensorEntityDescription

    def __init__(
        self,
        coordinator: ThermalBalanceCoordinator,
        entry: ConfigEntry,
        description: ThermalBalanceSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self.entity_description = description

        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Thermal Balance",
            model="Thermodynamics Hub",
        )

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return dynamic unit of measurement for monetary sensors."""
        key = self.entity_description.key
        if key in (SENSOR_AC_ENERGY_COST, SENSOR_SHADING_DAILY_SAVINGS):
            return self.coordinator.currency_symbol
        return self.entity_description.native_unit_of_measurement

    @property
    def native_value(self) -> float | None:
        """Return native value of sensor."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def icon(self) -> str | None:
        """Return dynamic icon based on sensor state and mode."""
        if self.entity_description.key == SENSOR_AC_HEAT_OUTPUT:
            return "mdi:fire" if self.coordinator.is_heating else "mdi:snowflake"
        return super().icon

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes for entity."""
        return self.coordinator.extra_attributes.get(self.entity_description.key)

    async def async_added_to_hass(self) -> None:
        """Handle entity addition to Home Assistant."""
        await super().async_added_to_hass()

        if self.entity_description.is_restorable:
            last_state = await self.async_get_last_state()
            if last_state is not None and last_state.state not in ("unknown", "unavailable"):
                try:
                    restored_val = float(last_state.state)

                    # Determine if last_state was updated on the current calendar day
                    now_date = dt_util.now().date()
                    is_same_day = False
                    if hasattr(last_state, "last_updated") and last_state.last_updated is not None:
                        last_updated = last_state.last_updated
                        tz = getattr(dt_util, "DEFAULT_TIME_ZONE", None)
                        if tz and hasattr(last_updated, "astimezone"):
                            is_same_day = (last_updated.astimezone(tz).date() == now_date)
                        elif hasattr(last_updated, "date"):
                            is_same_day = (last_updated.date() == now_date)

                    if self.entity_description.key == SENSOR_TOTAL_HEAT_ABSORBED:
                        self.coordinator.total_heat_absorbed = restored_val
                    elif self.entity_description.key == SENSOR_AC_THERMAL_ENERGY_TOTAL:
                        self.coordinator.ac_thermal_energy_total = restored_val
                    elif self.entity_description.key == SENSOR_EMPIRICAL_K_FACTOR:
                        self.coordinator.empirical_k_val = restored_val
                    elif self.entity_description.key == SENSOR_DAILY_THERMAL_BALANCE:
                        if is_same_day and last_state.attributes:
                            if "daily_heat_absorbed" in last_state.attributes:
                                self.coordinator.daily_heat_absorbed = float(last_state.attributes["daily_heat_absorbed"])
                            if "daily_ac_thermal_energy" in last_state.attributes:
                                self.coordinator.daily_ac_thermal_energy = float(last_state.attributes["daily_ac_thermal_energy"])
                            if "daily_ac_elec_kwh" in last_state.attributes:
                                self.coordinator.daily_ac_elec_kwh = float(last_state.attributes["daily_ac_elec_kwh"])
                            if "daily_shading_heat_saved_kwh" in last_state.attributes:
                                self.coordinator.daily_shading_heat_saved_kwh = float(last_state.attributes["daily_shading_heat_saved_kwh"])
                        else:
                            _LOGGER.debug("Daily thermal balance from previous day discarded on boot")

                    _LOGGER.debug("Restored %s = %f", self.entity_description.key, restored_val)
                    self.coordinator.recalculate()
                except (ValueError, TypeError):
                    pass
