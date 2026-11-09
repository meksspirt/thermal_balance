"""Button platform for Thermal Balance custom component."""
from __future__ import annotations

import logging
from typing import Any, Final

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BUTTON_RESET_DAILY, BUTTON_RESET_K_FACTOR, DOMAIN
from .coordinator import ThermalBalanceCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES: Final = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Thermal Balance button entities from a config entry."""
    coordinator: ThermalBalanceCoordinator = entry.runtime_data

    buttons = [
        ThermalBalanceResetDailyButton(coordinator, entry),
        ThermalBalanceResetKFactorButton(coordinator, entry),
    ]
    async_add_entities(buttons)


class ThermalBalanceButtonBase(
    CoordinatorEntity[ThermalBalanceCoordinator], ButtonEntity
):
    """Base class for Thermal Balance buttons."""

    def __init__(
        self,
        coordinator: ThermalBalanceCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_has_entity_name = True
        self._attr_translation_key = key
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Thermal Balance",
            model="Thermodynamics Hub",
        )


class ThermalBalanceResetDailyButton(ThermalBalanceButtonBase):
    """Button to immediately reset daily energy accumulators."""

    def __init__(
        self,
        coordinator: ThermalBalanceCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the reset daily button."""
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            key=BUTTON_RESET_DAILY,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Manual daily accumulators reset triggered via button")
        await self.coordinator.async_reset_daily()


class ThermalBalanceResetKFactorButton(ThermalBalanceButtonBase):
    """Button to reset empirical K-factor learning samples."""

    def __init__(
        self,
        coordinator: ThermalBalanceCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the reset K-factor button."""
        super().__init__(
            coordinator=coordinator,
            entry=entry,
            key=BUTTON_RESET_K_FACTOR,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Empirical K-factor recalibration reset triggered via button")
        await self.coordinator.async_reset_k_factor()
