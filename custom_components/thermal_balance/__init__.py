"""Thermal Balance Integration for Home Assistant."""
from __future__ import annotations

import logging
import os
from typing import Any

import voluptuous as vol

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import ServiceValidationError

from .const import (
    DOMAIN,
    SERVICE_CALCULATE_COOLING_NEEDS,
    SERVICE_RECALIBRATE_K_FACTOR,
    SERVICE_RESET_ACCUMULATORS,
)
from .coordinator import ThermalBalanceCoordinator
from .model import (
    CURTAIN_TYPE_FACTORS,
    RoomGeometry,
    ThermodynamicInputs,
    calculate_ac_performance,
    calculate_equilibrium_temperature,
    calculate_required_hvac_power,
    calculate_solar_radiation,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
    Platform.BUTTON,
    Platform.NUMBER,
]

# Configuration schema (Config Entry Only)
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

# Track whether the frontend card has been registered (once per HA session)
_FRONTEND_REGISTERED = False


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Register built-in Lovelace card static paths non-blockingly."""
    global _FRONTEND_REGISTERED  # noqa: PLW0603
    if _FRONTEND_REGISTERED:
        return

    card_path = os.path.join(os.path.dirname(__file__), "thermal-balance-card.js")
    echarts_path = os.path.join(os.path.dirname(__file__), "echarts.min.js")
    url_path = f"/{DOMAIN}/thermal-balance-card.js"
    url_echarts = f"/{DOMAIN}/echarts.min.js"

    # Non-blocking file existence check using executor job
    card_exists, echarts_exists = await hass.async_add_executor_job(
        lambda: (os.path.exists(card_path), os.path.exists(echarts_path))
    )

    if card_exists and echarts_exists:
        if hasattr(hass.http, "async_register_static_paths"):
            from homeassistant.components.http import StaticPathConfig
            await hass.http.async_register_static_paths([
                StaticPathConfig(url_path, card_path, False),
                StaticPathConfig(url_echarts, echarts_path, False),
            ])
        elif hasattr(hass.http, "register_static_path"):
            hass.http.register_static_path(url_path, card_path, cache_headers=False)
            hass.http.register_static_path(url_echarts, echarts_path, cache_headers=False)

        add_extra_js_url(hass, url_path)
        _FRONTEND_REGISTERED = True
        _LOGGER.info("Thermal Balance Lovelace card registered at %s", url_path)


RESET_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
})

CALCULATE_NEEDS_SCHEMA = vol.Schema({
    vol.Optional("entry_id"): cv.string,
    vol.Optional("target_temperature", default=23.0): vol.Coerce(float),
    vol.Optional("outdoor_temperature"): vol.Coerce(float),
    vol.Optional("solar_irradiance"): vol.Coerce(float),
    vol.Optional("curtains_closed", default=False): cv.boolean,
})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Thermal Balance component services."""
    await _async_register_frontend(hass)

    def _get_coordinators(call: ServiceCall) -> list[ThermalBalanceCoordinator]:
        entry_id = call.data.get("entry_id")
        coordinators: list[ThermalBalanceCoordinator] = []
        for entry in hass.config_entries.async_entries(DOMAIN):
            if hasattr(entry, "runtime_data") and isinstance(entry.runtime_data, ThermalBalanceCoordinator):
                if not entry_id or entry.entry_id == entry_id:
                    coordinators.append(entry.runtime_data)

        if not coordinators:
            if entry_id:
                raise ServiceValidationError(
                    f"Thermal Balance config entry {entry_id} was not found.",
                    translation_domain=DOMAIN,
                    translation_key="entry_not_found",
                    translation_placeholders={"entry_id": entry_id},
                )
            raise ServiceValidationError(
                "No active Thermal Balance integration instances found.",
                translation_domain=DOMAIN,
                translation_key="no_instances",
            )
        return coordinators

    async def handle_reset_accumulators(call: ServiceCall) -> None:
        coordinators = _get_coordinators(call)
        for coord in coordinators:
            await coord.async_reset_accumulators()

    async def handle_recalibrate_k_factor(call: ServiceCall) -> None:
        coordinators = _get_coordinators(call)
        for coord in coordinators:
            await coord.async_reset_k_factor()

    async def handle_calculate_cooling_needs(call: ServiceCall) -> ServiceResponse:
        coordinators = _get_coordinators(call)
        coord = coordinators[0] if coordinators else None

        t_target = float(call.data.get("target_temperature", 23.0))
        t_out = float(call.data["outdoor_temperature"]) if "outdoor_temperature" in call.data else (coord.t_out_val if coord else 30.0)
        solar = float(call.data["solar_irradiance"]) if "solar_irradiance" in call.data else (coord.solar_val if coord else 400.0)
        curtains_closed = bool(call.data.get("curtains_closed", False))

        geometry = coord.geometry if coord else RoomGeometry(20.0, 2.7, 3.0, 0.25, 0.3, 1.1)
        hlc = coord.hlc_closed if coord else geometry.hlc_theoretical

        curtain_type = coord.curtain_type if coord else "roller_gaps"
        curtain_factors = CURTAIN_TYPE_FACTORS.get(curtain_type, CURTAIN_TYPE_FACTORS["roller_gaps"])
        curtain_g = curtain_factors[0] if curtains_closed else 0.70

        window_azimuth = coord.window_azimuth if coord else 0.0
        sun_elevation = 0.0
        sun_azimuth = 180.0
        has_sun_position = False
        sun_state = hass.states.get("sun.sun")
        if sun_state is not None:
            try:
                sun_elevation = float(sun_state.attributes.get("elevation", 0.0))
                sun_azimuth = float(sun_state.attributes.get("azimuth", 180.0))
                has_sun_position = True
            except (ValueError, TypeError):
                pass

        (
            p_solar,
            _p_solar_direct,
            _p_solar_diffuse,
            _solar_aoi_deg,
            _solar_cos_aoi,
            _sun_is_direct,
        ) = calculate_solar_radiation(
            window_area=geometry.window_area,
            solar_irradiance=max(0.0, solar),
            curtain_g_factor=curtain_g,
            window_azimuth=window_azimuth,
            sun_elevation_deg=sun_elevation,
            sun_azimuth_deg=sun_azimuth,
            has_sun_position=has_sun_position,
        )

        p_req = calculate_required_hvac_power(
            t_target=t_target,
            t_out=t_out,
            p_solar=p_solar,
            hlc_total=hlc,
            is_heating=False,
        )
        t_eq = calculate_equilibrium_temperature(
            t_out=t_out,
            p_solar=p_solar,
            hlc_total=hlc,
        )

        ac_max = coord.ac_max_cooling if coord else 3350.0
        ac_airflow = coord.ac_airflow if coord else 370.0
        load_fraction = min(1.0, p_req / max(100.0, ac_max))

        model_inputs = ThermodynamicInputs(
            t_in=t_target,
            t_out=t_out,
            solar_irradiance=solar,
            ac_power=1000.0,
            curtains_closed=curtains_closed,
            curtain_type=curtain_type,
            window_azimuth=window_azimuth,
            sun_elevation_deg=sun_elevation,
            sun_azimuth_deg=sun_azimuth,
            has_sun_position=has_sun_position,
            is_heating=False,
        )
        ac_perf = calculate_ac_performance(model_inputs, ac_max, ac_airflow)
        cop_est = ac_perf.cop if ac_perf.cop > 0 else 3.2
        elec_power = p_req / cop_est if cop_est > 0 else 0.0

        return {
            "required_power_w": round(p_req, 1),
            "equilibrium_temperature_c": round(t_eq, 1),
            "cooling_load_fraction": round(load_fraction, 2),
            "estimated_cop": round(cop_est, 2),
            "estimated_elec_power_w": round(elec_power, 1),
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_ACCUMULATORS,
        handle_reset_accumulators,
        schema=RESET_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RECALIBRATE_K_FACTOR,
        handle_recalibrate_k_factor,
        schema=RESET_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CALCULATE_COOLING_NEEDS,
        handle_calculate_cooling_needs,
        schema=CALCULATE_NEEDS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Thermal Balance from a config entry."""
    await _async_register_frontend(hass)

    coordinator = ThermalBalanceCoordinator(hass, entry)
    await coordinator.async_start()

    # Store coordinator directly in runtime_data (HA 2024.4+ standard)
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: ThermalBalanceCoordinator = entry.runtime_data
    if coordinator:
        await coordinator.async_stop()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    coordinator: ThermalBalanceCoordinator = getattr(entry, "runtime_data", None)
    if coordinator and hasattr(coordinator, "check_options_need_reload") and coordinator.check_options_need_reload(entry.options):
        await hass.config_entries.async_reload(entry.entry_id)
    elif coordinator and hasattr(coordinator, "update_runtime_options"):
        coordinator.update_runtime_options(entry.options)
    else:
        await hass.config_entries.async_reload(entry.entry_id)
