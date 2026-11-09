"""Select platform for Thermal Balance custom component."""
from __future__ import annotations

import logging
from typing import Any, Final

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CURTAIN_TYPES,
    DOMAIN,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOLING,
    HVAC_MODE_HEATING,
    HVAC_MODES,
    SELECT_CURTAIN_TYPE,
    SELECT_HVAC_MODE,
)
from .coordinator import ThermalBalanceCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES: Final = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Thermal Balance select entities from a config entry."""
    coordinator: ThermalBalanceCoordinator = entry.runtime_data

    async_add_entities([
        ThermalBalanceHVACModeSelect(coordinator, entry),
        ThermalBalanceCurtainTypeSelect(coordinator, entry),
    ])


class ThermalBalanceHVACModeSelect(
    CoordinatorEntity[ThermalBalanceCoordinator], RestoreEntity, SelectEntity
):
    """Representation of Thermal Balance HVAC Mode selector in Device Controls."""

    def __init__(
        self,
        coordinator: ThermalBalanceCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{SELECT_HVAC_MODE}"
        self._attr_has_entity_name = True
        self._attr_translation_key = "hvac_mode"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_options = HVAC_MODES
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Thermal Balance",
            model="Thermodynamics Hub",
        )

    @property
    def icon(self) -> str:
        """Return dynamic icon based on current mode."""
        mode = self.coordinator.hvac_mode
        if mode == HVAC_MODE_HEATING or (mode == HVAC_MODE_AUTO and self.coordinator.is_heating):
            return "mdi:fire"
        if mode == HVAC_MODE_COOLING or (mode == HVAC_MODE_AUTO and not self.coordinator.is_heating):
            return "mdi:snowflake"
        return "mdi:hvac"

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        return self.coordinator.hvac_mode

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in HVAC_MODES:
            _LOGGER.warning("Invalid HVAC mode selected: %s", option)
            return
        await self.coordinator.async_set_hvac_mode(option)
        if self.entry and hasattr(self.hass, "config_entries") and hasattr(self.hass.config_entries, "async_update_entry"):
            new_options = {**self.entry.options, SELECT_HVAC_MODE: option}
            self.hass.config_entries.async_update_entry(self.entry, options=new_options)

    async def async_added_to_hass(self) -> None:
        """Handle entity restoration."""
        await super().async_added_to_hass()
        if SELECT_HVAC_MODE not in self.entry.options and SELECT_HVAC_MODE not in self.entry.data:
            last_state = await self.async_get_last_state()
            if last_state is not None and last_state.state in HVAC_MODES:
                await self.coordinator.async_set_hvac_mode(last_state.state)
                _LOGGER.debug("Restored HVAC mode: %s", last_state.state)


class ThermalBalanceCurtainTypeSelect(
    CoordinatorEntity[ThermalBalanceCoordinator], RestoreEntity, SelectEntity
):
    """Representation of Thermal Balance Curtain / Shading Type selector in Device Controls."""

    def __init__(
        self,
        coordinator: ThermalBalanceCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the curtain type select entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{SELECT_CURTAIN_TYPE}"
        self._attr_has_entity_name = True
        self._attr_translation_key = "curtain_type"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_options = CURTAIN_TYPES
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Thermal Balance",
            model="Thermodynamics Hub",
        )

    @property
    def current_option(self) -> str | None:
        """Return current selected option."""
        return self.coordinator.curtain_type

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in CURTAIN_TYPES:
            _LOGGER.warning("Invalid curtain type selected: %s", option)
            return
        await self.coordinator.async_set_curtain_type(option)
        if self.entry and hasattr(self.hass, "config_entries") and hasattr(self.hass.config_entries, "async_update_entry"):
            new_options = {**self.entry.options, SELECT_CURTAIN_TYPE: option}
            self.hass.config_entries.async_update_entry(self.entry, options=new_options)

    async def async_added_to_hass(self) -> None:
        """Handle entity restoration."""
        await super().async_added_to_hass()
        if SELECT_CURTAIN_TYPE not in self.entry.options and SELECT_CURTAIN_TYPE not in self.entry.data:
            last_state = await self.async_get_last_state()
            if last_state is not None and last_state.state in CURTAIN_TYPES:
                await self.coordinator.async_set_curtain_type(last_state.state)
                _LOGGER.debug("Restored curtain type: %s", last_state.state)

