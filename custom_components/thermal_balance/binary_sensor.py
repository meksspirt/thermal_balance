"""Binary sensor platform for Thermal Balance custom component."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Final

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BINARY_SENSOR_INSUFFICIENT_COOLING_CAPACITY,
    BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS,
    BINARY_SENSOR_RECOMMEND_OPEN_WINDOW,
    DOMAIN,
    SENSOR_AC_CARNOT_COP,
    SENSOR_INSTANT_HEAT_GAIN,
    SENSOR_REQUIRED_AC_POWER,
)
from .coordinator import ThermalBalanceCoordinator
from .model import CURTAIN_TYPE_FACTORS

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES: Final = 0


@dataclass(frozen=True)
class ThermalBalanceBinarySensorDescription(BinarySensorEntityDescription):
    """Class describing Thermal Balance binary sensor entities."""


BINARY_SENSOR_TYPES: tuple[ThermalBalanceBinarySensorDescription, ...] = (
    ThermalBalanceBinarySensorDescription(
        key=BINARY_SENSOR_RECOMMEND_OPEN_WINDOW,
        translation_key=BINARY_SENSOR_RECOMMEND_OPEN_WINDOW,
    ),
    ThermalBalanceBinarySensorDescription(
        key=BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS,
        translation_key=BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS,
    ),
    ThermalBalanceBinarySensorDescription(
        key=BINARY_SENSOR_INSUFFICIENT_COOLING_CAPACITY,
        translation_key=BINARY_SENSOR_INSUFFICIENT_COOLING_CAPACITY,
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Thermal Balance binary sensors from a config entry."""
    coordinator: ThermalBalanceCoordinator = entry.runtime_data

    async_add_entities(
        ThermalBalanceBinarySensor(coordinator, description, entry)
        for description in BINARY_SENSOR_TYPES
    )


class ThermalBalanceBinarySensor(CoordinatorEntity[ThermalBalanceCoordinator], BinarySensorEntity):
    """Representation of a Thermal Balance binary sensor."""

    entity_description: ThermalBalanceBinarySensorDescription

    def __init__(
        self,
        coordinator: ThermalBalanceCoordinator,
        description: ThermalBalanceBinarySensorDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
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
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return bool(self.coordinator.data.get(self.entity_description.key, False))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes for advice and financial impact."""
        key = self.entity_description.key
        attrs: dict[str, Any] = {}
        if key == BINARY_SENSOR_RECOMMEND_OPEN_WINDOW:
            t_in = self.coordinator.t_in_val
            t_out = self.coordinator.t_out_val
            if self.is_on:
                attrs["advice"] = f"Outdoor air ({t_out:.1f}°C) is cooler than indoor ({t_in:.1f}°C). Open window for free cooling!"
            else:
                attrs["advice"] = "Outdoor temperature is higher than indoor. Keep window closed."
            attrs["temp_difference_c"] = round(t_in - t_out, 1)

        elif key == BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS:
            solar = self.coordinator.solar_val
            rate = self.coordinator.electricity_rate
            symbol = self.coordinator.currency_symbol

            curtain_factors = CURTAIN_TYPE_FACTORS.get(
                self.coordinator.curtain_type, CURTAIN_TYPE_FACTORS["roller_gaps"]
            )
            saved_fraction = curtain_factors[1]

            # Use AOI-calculated incident solar radiation on window
            heat_gain_attrs = self.coordinator.extra_attributes.get(SENSOR_INSTANT_HEAT_GAIN, {})
            p_solar_current = heat_gain_attrs.get("p_solar_w", 0.0)
            g_current = heat_gain_attrs.get("g_solar_factor", 0.70)
            incident_solar_w = p_solar_current / max(0.01, g_current) if g_current > 0 else 0.0
            pot_w = incident_solar_w * saved_fraction

            cop_raw = self.coordinator.data.get(SENSOR_AC_CARNOT_COP, 3.2)
            cop = cop_raw if cop_raw and cop_raw > 0 else 3.2
            saved_kwh_day = (pot_w / cop / 1000.0) * 12.0
            saved_cost_day = saved_kwh_day * rate

            if self.is_on:
                attrs["advice"] = f"High solar radiation ({solar:.0f} W/m²). Close curtains to reduce solar heat gain!"
            else:
                attrs["advice"] = "Solar radiation is low or curtains are already closed."
            attrs["solar_radiation_w_m2"] = round(solar, 1)
            attrs["potential_heat_reduction_w"] = round(pot_w, 0)
            attrs["potential_daily_savings"] = f"{saved_cost_day:.2f} {symbol}/day"

        elif key == BINARY_SENSOR_INSUFFICIENT_COOLING_CAPACITY:
            is_heating = self.coordinator.is_heating
            ac_max = self.coordinator.ac_max_cooling * (1.20 if is_heating else 1.0)
            req_power = self.coordinator.data.get(SENSOR_REQUIRED_AC_POWER, 0.0)
            if self.is_on:
                attrs["advice"] = (
                    f"Room thermal load ({req_power:.0f} W) exceeds rated equipment capacity ({ac_max:.0f} W). "
                    "Close curtains or reduce ventilation to maintain comfort."
                )
            else:
                attrs["advice"] = f"Equipment capacity ({ac_max:.0f} W) is sufficient for current thermal load."
            attrs["rated_capacity_w"] = round(ac_max, 0)
            attrs["required_power_w"] = round(req_power, 0)

        return attrs
