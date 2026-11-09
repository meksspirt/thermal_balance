"""Number platform for Thermal Balance custom component."""
from __future__ import annotations

import logging
from typing import Any, Final

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NUMBER_ELECTRICITY_RATE
from .coordinator import ThermalBalanceCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES: Final = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Thermal Balance number entities from a config entry."""
    coordinator: ThermalBalanceCoordinator = entry.runtime_data

    async_add_entities([ThermalBalanceElectricityRateNumber(coordinator, entry)])


class ThermalBalanceElectricityRateNumber(
    CoordinatorEntity[ThermalBalanceCoordinator], RestoreEntity, NumberEntity
):
    """Number entity for dynamic electricity rate adjustment."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0.0
    _attr_native_max_value = 100.0
    _attr_native_step = 0.01

    def __init__(
        self,
        coordinator: ThermalBalanceCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{NUMBER_ELECTRICITY_RATE}"
        self._attr_has_entity_name = True
        self._attr_translation_key = NUMBER_ELECTRICITY_RATE
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Thermal Balance",
            model="Thermodynamics Hub",
        )

    @property
    def native_unit_of_measurement(self) -> str:
        """Return dynamic currency unit per kWh."""
        return f"{self.coordinator.currency_symbol}/kWh"

    @property
    def native_value(self) -> float:
        """Return current electricity rate."""
        return self.coordinator.electricity_rate

    async def async_set_native_value(self, value: float) -> None:
        """Update electricity rate."""
        await self.coordinator.async_set_electricity_rate(value)
        if self.entry and hasattr(self.hass, "config_entries") and hasattr(self.hass.config_entries, "async_update_entry"):
            new_options = {**self.entry.options, NUMBER_ELECTRICITY_RATE: value}
            self.hass.config_entries.async_update_entry(self.entry, options=new_options)

    async def async_added_to_hass(self) -> None:
        """Restore state across HA restarts."""
        await super().async_added_to_hass()
        if NUMBER_ELECTRICITY_RATE not in self.entry.options and NUMBER_ELECTRICITY_RATE not in self.entry.data:
            last_state = await self.async_get_last_state()
            if last_state is not None and last_state.state not in ("unknown", "unavailable"):
                try:
                    restored_val = float(last_state.state)
                    await self.coordinator.async_set_electricity_rate(restored_val)
                    _LOGGER.debug("Restored dynamic electricity rate: %s", restored_val)
                except (ValueError, TypeError):
                    pass
