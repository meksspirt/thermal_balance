"""Coordinator for Thermal Balance custom component."""
from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
    async_track_time_interval,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    BINARY_SENSOR_INSUFFICIENT_COOLING_CAPACITY,
    BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS,
    BINARY_SENSOR_RECOMMEND_OPEN_WINDOW,
    CONF_AC_AIRFLOW,
    CONF_AC_MAX_COOLING,
    CONF_CEILING_HEIGHT,
    CONF_CURRENCY_SYMBOL,
    CONF_CURTAIN_TYPE,
    CONF_ELECTRICITY_RATE,
    CONF_EXTERNAL_WALLS_FRACTION,
    CONF_HVAC_MODE,
    CONF_ILLUMINANCE_THRESHOLD,
    CONF_ROOM_AREA,
    CONF_SENSOR_AC_POWER,
    CONF_SENSOR_CLIMATE,
    CONF_SENSOR_ILLUMINANCE,
    CONF_SENSOR_RH_IN,
    CONF_SENSOR_RH_OUT,
    CONF_SENSOR_SOLAR,
    CONF_SENSOR_T_AC_EXIT,
    CONF_SENSOR_T_IN,
    CONF_SENSOR_T_OUT,
    CONF_SENSOR_WEATHER,
    CONF_SENSOR_WIND_DIRECTION,
    CONF_SENSOR_WIND_SPEED,
    CONF_SENSOR_WINDOW,
    CONF_U_WALL,
    CONF_U_WINDOW,
    CONF_USE_EMPIRICAL_HLC,
    CONF_WINDOW_AREA,
    CONF_WINDOW_AZIMUTH,
    DEFAULT_AC_AIRFLOW,
    DEFAULT_AC_MAX_COOLING,
    DEFAULT_CEILING_HEIGHT,
    DEFAULT_CURTAIN_TYPE,
    DEFAULT_ELECTRICITY_RATE,
    DEFAULT_EXTERNAL_WALLS_FRACTION,
    DEFAULT_HVAC_MODE,
    DEFAULT_ILLUMINANCE_THRESHOLD,
    DEFAULT_ROOM_AREA,
    DEFAULT_U_WALL,
    DEFAULT_U_WINDOW,
    DEFAULT_USE_EMPIRICAL_HLC,
    DEFAULT_WINDOW_AREA,
    DEFAULT_WINDOW_AZIMUTH,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOLING,
    HVAC_MODE_HEATING,
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

RELOAD_CONFIG_KEYS = {
    CONF_ROOM_AREA,
    CONF_CEILING_HEIGHT,
    CONF_WINDOW_AREA,
    CONF_EXTERNAL_WALLS_FRACTION,
    CONF_U_WALL,
    CONF_U_WINDOW,
    CONF_WINDOW_AZIMUTH,
    CONF_USE_EMPIRICAL_HLC,
    CONF_AC_MAX_COOLING,
    CONF_AC_AIRFLOW,
    CONF_ILLUMINANCE_THRESHOLD,
    CONF_CURRENCY_SYMBOL,
    CONF_SENSOR_T_IN,
    CONF_SENSOR_T_OUT,
    CONF_SENSOR_AC_POWER,
    CONF_SENSOR_CLIMATE,
    CONF_SENSOR_SOLAR,
    CONF_SENSOR_WEATHER,
    CONF_SENSOR_WINDOW,
    CONF_SENSOR_ILLUMINANCE,
    CONF_SENSOR_T_AC_EXIT,
    CONF_SENSOR_RH_IN,
    CONF_SENSOR_RH_OUT,
    CONF_SENSOR_WIND_SPEED,
    CONF_SENSOR_WIND_DIRECTION,
}
from .engine import (
    EngineCycleInputs,
    ThermalEngine,
    normalize_wind_speed,
    parse_cloud_coverage,
    resolve_curtains_closed,
    resolve_is_heating,
)
from .model import (
    RoomGeometry,
    estimate_solar_irradiance,
)

_LOGGER = logging.getLogger(__name__)


def _safe_float(val: Any, default: float) -> float:
    """Safely convert value to float."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


class ThermalBalanceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator bridging Home Assistant entity events to the ThermalEngine."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Thermal Balance ({entry.title})",
            always_update=False,
        )
        self.entry = entry

        options = entry.options
        data = entry.data

        # Room geometry
        room_area = _safe_float(options.get(CONF_ROOM_AREA, data.get(CONF_ROOM_AREA)), DEFAULT_ROOM_AREA)
        ceiling_height = _safe_float(options.get(CONF_CEILING_HEIGHT, data.get(CONF_CEILING_HEIGHT)), DEFAULT_CEILING_HEIGHT)
        window_area = _safe_float(options.get(CONF_WINDOW_AREA, data.get(CONF_WINDOW_AREA)), DEFAULT_WINDOW_AREA)
        external_walls_fraction = _safe_float(
            options.get(CONF_EXTERNAL_WALLS_FRACTION, data.get(CONF_EXTERNAL_WALLS_FRACTION)),
            DEFAULT_EXTERNAL_WALLS_FRACTION,
        )
        u_wall = _safe_float(options.get(CONF_U_WALL, data.get(CONF_U_WALL)), DEFAULT_U_WALL)
        u_window = _safe_float(options.get(CONF_U_WINDOW, data.get(CONF_U_WINDOW)), DEFAULT_U_WINDOW)

        self.geometry = RoomGeometry(
            room_area=room_area,
            ceiling_height=ceiling_height,
            window_area=window_area,
            external_walls_fraction=external_walls_fraction,
            u_wall=u_wall,
            u_window=u_window,
        )

        self.ac_max_cooling: float = _safe_float(options.get(CONF_AC_MAX_COOLING, data.get(CONF_AC_MAX_COOLING)), DEFAULT_AC_MAX_COOLING)
        self.ac_airflow: float = _safe_float(options.get(CONF_AC_AIRFLOW, data.get(CONF_AC_AIRFLOW)), DEFAULT_AC_AIRFLOW)

        # Entity IDs
        self.sensor_t_in: str = options.get(CONF_SENSOR_T_IN, data.get(CONF_SENSOR_T_IN, ""))
        self.sensor_t_out: str = options.get(CONF_SENSOR_T_OUT, data.get(CONF_SENSOR_T_OUT, ""))
        self.sensor_t_ac_exit: str = options.get(CONF_SENSOR_T_AC_EXIT, data.get(CONF_SENSOR_T_AC_EXIT, ""))
        self.sensor_rh_in: str = options.get(CONF_SENSOR_RH_IN, data.get(CONF_SENSOR_RH_IN, ""))
        self.sensor_rh_out: str = options.get(CONF_SENSOR_RH_OUT, data.get(CONF_SENSOR_RH_OUT, ""))
        self.sensor_solar: str = options.get(CONF_SENSOR_SOLAR, data.get(CONF_SENSOR_SOLAR, ""))
        self.sensor_weather: str = options.get(CONF_SENSOR_WEATHER, data.get(CONF_SENSOR_WEATHER, ""))
        self.sensor_ac_power: str = options.get(CONF_SENSOR_AC_POWER, data.get(CONF_SENSOR_AC_POWER, ""))
        self.sensor_climate: str = options.get(CONF_SENSOR_CLIMATE, data.get(CONF_SENSOR_CLIMATE, ""))
        self.hvac_mode: str = str(options.get(CONF_HVAC_MODE, data.get(CONF_HVAC_MODE, DEFAULT_HVAC_MODE)))
        self.is_heating: bool = (self.hvac_mode == HVAC_MODE_HEATING)
        self.sensor_window: str = options.get(CONF_SENSOR_WINDOW, data.get(CONF_SENSOR_WINDOW, ""))
        self.sensor_illuminance: str = options.get(CONF_SENSOR_ILLUMINANCE, data.get(CONF_SENSOR_ILLUMINANCE, ""))
        self.sensor_wind_speed: str = options.get(CONF_SENSOR_WIND_SPEED, data.get(CONF_SENSOR_WIND_SPEED, ""))
        self.sensor_wind_direction: str = options.get(CONF_SENSOR_WIND_DIRECTION, data.get(CONF_SENSOR_WIND_DIRECTION, ""))
        self.window_azimuth: float = _safe_float(options.get(CONF_WINDOW_AZIMUTH, data.get(CONF_WINDOW_AZIMUTH)), DEFAULT_WINDOW_AZIMUTH)
        self.illuminance_threshold: float = _safe_float(
            options.get(CONF_ILLUMINANCE_THRESHOLD, data.get(CONF_ILLUMINANCE_THRESHOLD)),
            DEFAULT_ILLUMINANCE_THRESHOLD,
        )

        self.electricity_rate: float = _safe_float(
            options.get(CONF_ELECTRICITY_RATE, data.get(CONF_ELECTRICITY_RATE, DEFAULT_ELECTRICITY_RATE)),
            DEFAULT_ELECTRICITY_RATE,
        )

        # Currency symbol
        hass_currency = getattr(hass.config, "currency", None) or "USD"
        raw_currency = options.get(CONF_CURRENCY_SYMBOL, data.get(CONF_CURRENCY_SYMBOL))
        self.currency_symbol: str = str(raw_currency) if raw_currency else hass_currency

        self.curtain_type: str = str(options.get(CONF_CURTAIN_TYPE, data.get(CONF_CURTAIN_TYPE, DEFAULT_CURTAIN_TYPE)))
        self.use_empirical_hlc: bool = bool(options.get(CONF_USE_EMPIRICAL_HLC, data.get(CONF_USE_EMPIRICAL_HLC, DEFAULT_USE_EMPIRICAL_HLC)))

        # Snapshot options requiring integration reload vs live in-place update
        self._config_signature = {k: options.get(k, data.get(k)) for k in RELOAD_CONFIG_KEYS}

        # Pure Python Domain Engine
        self.engine: ThermalEngine = ThermalEngine(self.geometry)

        # Current sensor input caches
        self.t_in_val: float = 20.0
        self.t_out_val: float = 20.0
        self.t_ac_exit_val: float = 20.0
        self.rh_in_val: float = 50.0
        self.rh_out_val: float = 60.0
        self.solar_val: float = 0.0
        self.ac_power_val: float = 0.0
        self.window_is_open: bool = False
        self.illuminance_val: float = 500.0
        self.curtains_closed: bool = False
        self.curtains_note: str | None = None
        self.wind_speed_ms: float = 0.0
        self.wind_dir_deg: float = 0.0
        self.dt_dt_c_per_h: float = 0.0
        self.p_storage_w: float = 0.0
        self.p_wall_dynamic_w: float = 0.0

        # State and attribute storage
        self.extra_attributes: dict[str, dict[str, Any]] = {}
        self._unsub_track: list[Any] = []
        self._unavailable_mandatory_sensors: set[str] = set()
        self.last_update_success: bool = True

        self.data: dict[str, Any] = {
            SENSOR_INSTANT_HEAT_GAIN: 0.0,
            SENSOR_AC_HEAT_OUTPUT: 0.0,
            SENSOR_INSTANT_NET_BALANCE: 0.0,
            SENSOR_AC_CARNOT_COP: 0.0,
            SENSOR_TIME_TO_1DEG: 0.0,
            SENSOR_DAILY_THERMAL_BALANCE: 0.0,
            SENSOR_NET_THERMAL_BALANCE: 0.0,
            SENSOR_TOTAL_HEAT_ABSORBED: 0.0,
            SENSOR_AC_THERMAL_ENERGY_TOTAL: 0.0,
            SENSOR_AC_CONDENSATION_RATE: 0.0,
            SENSOR_EMPIRICAL_K_FACTOR: round(self.geometry.hlc_theoretical, 2),
            SENSOR_EQUILIBRIUM_TEMPERATURE: 20.0,
            SENSOR_REQUIRED_AC_POWER: 0.0,
            SENSOR_AC_ENERGY_COST: 0.0,
            SENSOR_SHADING_DAILY_SAVINGS: 0.0,
            BINARY_SENSOR_RECOMMEND_OPEN_WINDOW: False,
            BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS: False,
            BINARY_SENSOR_INSUFFICIENT_COOLING_CAPACITY: False,
        }

    def check_options_need_reload(self, new_options: dict[str, Any]) -> bool:
        """Check if newly updated options require reloading the entire integration."""
        for key in RELOAD_CONFIG_KEYS:
            if key in new_options and new_options[key] != self._config_signature.get(key):
                return True
        return False

    def update_runtime_options(self, new_options: dict[str, Any]) -> None:
        """Update runtime configurable options without reloading."""
        if CONF_HVAC_MODE in new_options:
            self.hvac_mode = str(new_options[CONF_HVAC_MODE])
        if CONF_CURTAIN_TYPE in new_options:
            self.curtain_type = str(new_options[CONF_CURTAIN_TYPE])
        if CONF_ELECTRICITY_RATE in new_options:
            self.electricity_rate = _safe_float(new_options[CONF_ELECTRICITY_RATE], self.electricity_rate)
        self.recalculate()

    # Backward-compatible property delegates for energy accumulators
    @property
    def total_heat_absorbed(self) -> float:
        """Total heat absorbed in kWh."""
        return self.engine.accumulator.total_heat_absorbed

    @total_heat_absorbed.setter
    def total_heat_absorbed(self, value: float) -> None:
        self.engine.accumulator.total_heat_absorbed = value

    @property
    def ac_thermal_energy_total(self) -> float:
        """Total AC thermal energy output in kWh."""
        return self.engine.accumulator.ac_thermal_energy_total

    @ac_thermal_energy_total.setter
    def ac_thermal_energy_total(self, value: float) -> None:
        self.engine.accumulator.ac_thermal_energy_total = value

    @property
    def daily_heat_absorbed(self) -> float:
        """Daily heat absorbed in kWh."""
        return self.engine.accumulator.daily_heat_absorbed

    @daily_heat_absorbed.setter
    def daily_heat_absorbed(self, value: float) -> None:
        self.engine.accumulator.daily_heat_absorbed = value

    @property
    def daily_ac_thermal_energy(self) -> float:
        """Daily AC thermal energy in kWh."""
        return self.engine.accumulator.daily_ac_thermal_energy

    @daily_ac_thermal_energy.setter
    def daily_ac_thermal_energy(self, value: float) -> None:
        self.engine.accumulator.daily_ac_thermal_energy = value

    @property
    def daily_ac_elec_kwh(self) -> float:
        """Daily AC electricity consumption in kWh."""
        return self.engine.accumulator.daily_ac_elec_kwh

    @daily_ac_elec_kwh.setter
    def daily_ac_elec_kwh(self, value: float) -> None:
        self.engine.accumulator.daily_ac_elec_kwh = value

    @property
    def daily_shading_heat_saved_kwh(self) -> float:
        """Daily heat saved by shading in kWh."""
        return self.engine.accumulator.daily_shading_heat_saved_kwh

    @daily_shading_heat_saved_kwh.setter
    def daily_shading_heat_saved_kwh(self, value: float) -> None:
        self.engine.accumulator.daily_shading_heat_saved_kwh = value

    @property
    def last_update_time(self) -> datetime | None:
        """Last Riemann integration timestamp."""
        return self.engine.accumulator.last_update_time

    @last_update_time.setter
    def last_update_time(self, value: datetime | None) -> None:
        self.engine.accumulator.last_update_time = value

    @property
    def last_daily_reset(self) -> datetime | None:
        """Last daily reset timestamp."""
        return self.engine.accumulator.last_daily_reset

    @last_daily_reset.setter
    def last_daily_reset(self, value: datetime | None) -> None:
        self.engine.accumulator.last_daily_reset = value

    # Backward-compatible property delegates for K-factor calibrator
    @property
    def empirical_k_val(self) -> float:
        """Empirical K-factor (HLC) in W/K."""
        return self.engine.calibrator.empirical_k_val

    @empirical_k_val.setter
    def empirical_k_val(self, value: float) -> None:
        self.engine.calibrator.empirical_k_val = value

    @property
    def hlc_closed(self) -> float:
        """Active closed-window Heat Loss Coefficient in W/K."""
        return self.engine.calibrator.hlc_closed

    @hlc_closed.setter
    def hlc_closed(self, value: float) -> None:
        self.engine.calibrator.hlc_closed = value

    @property
    def _k_samples_count(self) -> int:
        """Number of calibration samples recorded."""
        return self.engine.calibrator.samples_count

    @_k_samples_count.setter
    def _k_samples_count(self, value: int) -> None:
        self.engine.calibrator.samples_count = value

    @property
    def _last_k_calibration_time(self) -> datetime | None:
        """Timestamp of the last K-factor calibration."""
        return self.engine.calibrator.last_calibration_time

    @_last_k_calibration_time.setter
    def _last_k_calibration_time(self, value: datetime | None) -> None:
        self.engine.calibrator.last_calibration_time = value

    @property
    def _t_in_history(self) -> deque[tuple[datetime, float]]:
        """Temperature history deque for regression."""
        return self.engine.history_tracker.history

    def _calculate_t_in_derivative(self, now: datetime) -> float:
        """Calculate indoor temperature derivative dT/dt in °C/hour."""
        return self.engine.history_tracker.update(now, self.t_in_val)

    async def async_set_hvac_mode(self, mode: str) -> None:
        """Set HVAC operation mode."""
        if mode in (HVAC_MODE_COOLING, HVAC_MODE_HEATING, HVAC_MODE_AUTO):
            self.hvac_mode = mode
            self.recalculate()

    async def async_set_curtain_type(self, curtain_type: str) -> None:
        """Set window curtain shading type."""
        self.curtain_type = curtain_type
        self.recalculate()

    async def async_set_electricity_rate(self, rate: float) -> None:
        """Set dynamic electricity rate."""
        self.electricity_rate = max(0.0, float(rate))
        self.recalculate()

    async def async_reset_daily(self) -> None:
        """Reset daily energy and financial accumulators."""
        self.engine.accumulator.reset_daily(dt_util.now())
        self.recalculate()

    async def async_reset_k_factor(self) -> None:
        """Reset empirical K-factor learning samples."""
        self.engine.calibrator.reset(self.geometry.hlc_theoretical)
        self.recalculate()

    async def async_reset_accumulators(self) -> None:
        """Reset both daily and all-time accumulators."""
        self.engine.accumulator.reset_all(dt_util.now())
        self.recalculate()

    @property
    def has_solar_sensor(self) -> bool:
        """Check if a solar irradiance sensor entity ID is configured."""
        return bool(self.sensor_solar and self.sensor_solar.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    @property
    def has_weather_sensor(self) -> bool:
        """Check if a weather entity ID is configured."""
        return bool(self.sensor_weather and self.sensor_weather.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    @property
    def has_climate_sensor(self) -> bool:
        """Check if a climate thermostat entity ID is configured."""
        return bool(self.sensor_climate and self.sensor_climate.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    @property
    def has_window_sensor(self) -> bool:
        """Check if a valid window binary_sensor entity ID is configured."""
        return bool(self.sensor_window and self.sensor_window.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    @property
    def has_t_ac_exit_sensor(self) -> bool:
        """Check if AC louver exit temperature sensor entity ID is configured."""
        return bool(self.sensor_t_ac_exit and self.sensor_t_ac_exit.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    @property
    def has_rh_in_sensor(self) -> bool:
        """Check if indoor humidity sensor entity ID is configured."""
        return bool(self.sensor_rh_in and self.sensor_rh_in.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    @property
    def has_rh_out_sensor(self) -> bool:
        """Check if outdoor humidity sensor entity ID is configured."""
        return bool(self.sensor_rh_out and self.sensor_rh_out.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    @property
    def has_illuminance_sensor(self) -> bool:
        """Check if illuminance sensor entity ID is configured."""
        return bool(self.sensor_illuminance and self.sensor_illuminance.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    @property
    def has_wind_speed_sensor(self) -> bool:
        """Check if wind speed sensor entity ID is configured."""
        return bool(self.sensor_wind_speed and self.sensor_wind_speed.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    @property
    def has_wind_dir_sensor(self) -> bool:
        """Check if wind direction sensor entity ID is configured."""
        return bool(self.sensor_wind_direction and self.sensor_wind_direction.strip().lower() not in ("", "none", "null", "unknown", "unavailable"))

    async def async_start(self) -> None:
        """Start listening to input state changes, interval timer, and midnight reset."""
        tracked_entities = [
            entity for entity in [
                self.sensor_t_in,
                self.sensor_t_out,
                self.sensor_t_ac_exit,
                self.sensor_rh_in,
                self.sensor_rh_out,
                self.sensor_solar,
                self.sensor_weather,
                self.sensor_ac_power,
                self.sensor_window,
                self.sensor_illuminance,
                self.sensor_wind_speed,
                self.sensor_wind_direction,
                self.sensor_climate,
                "sun.sun",
            ] if entity
        ]

        if tracked_entities:
            unsub_state = async_track_state_change_event(
                self.hass, tracked_entities, self._async_handle_state_change
            )
            self._unsub_track.append(unsub_state)

        unsub_midnight = async_track_time_change(
            self.hass, self._async_handle_midnight_reset, hour=0, minute=0, second=0
        )
        self._unsub_track.append(unsub_midnight)

        unsub_interval = async_track_time_interval(
            self.hass, self._async_handle_periodic_update, timedelta(seconds=30)
        )
        self._unsub_track.append(unsub_interval)

        self._read_initial_states()
        self.recalculate()

    async def async_stop(self) -> None:
        """Stop tracking events."""
        for unsub in self._unsub_track:
            unsub()
        self._unsub_track.clear()

    @callback
    def _read_initial_states(self) -> None:
        """Read initial state of sensors from Hass state machine."""
        mandatory = (self.sensor_t_in, self.sensor_t_out, self.sensor_ac_power)
        self._unavailable_mandatory_sensors.clear()
        for eid in mandatory:
            state = self.hass.states.get(eid)
            if state is None or state.state in ("unknown", "unavailable"):
                self._unavailable_mandatory_sensors.add(eid)
                _LOGGER.warning(
                    "Mandatory sensor %s is unavailable (state: %s)",
                    eid,
                    getattr(state, "state", None),
                )

        self.last_update_success = len(self._unavailable_mandatory_sensors) == 0

        self.t_in_val = self._get_float_state(self.sensor_t_in, 20.0)
        self.t_out_val = self._get_float_state(self.sensor_t_out, 20.0)
        self.t_ac_exit_val = self._get_float_state(self.sensor_t_ac_exit, self.t_in_val)
        self.rh_in_val = self._get_float_state(self.sensor_rh_in, 50.0)
        self.rh_out_val = self._get_float_state(self.sensor_rh_out, 60.0)
        self.solar_val = self._get_float_state(self.sensor_solar, 0.0)
        self.ac_power_val = self._get_float_state(self.sensor_ac_power, 0.0)

        if self.has_window_sensor:
            self.window_is_open = self._get_bool_state(self.sensor_window, False)
        else:
            self.window_is_open = False

        if self.has_illuminance_sensor:
            self.illuminance_val = self._get_float_state(self.sensor_illuminance, 500.0)
            self.curtains_closed = (self.illuminance_val < self.illuminance_threshold)

        if self.has_wind_speed_sensor:
            state = self.hass.states.get(self.sensor_wind_speed)
            val = self._get_float_state(self.sensor_wind_speed, 0.0)
            unit = state.attributes.get("unit_of_measurement") if state else None
            self.wind_speed_ms = normalize_wind_speed(val, unit)

        if self.has_wind_dir_sensor:
            self.wind_dir_deg = self._get_float_state(self.sensor_wind_direction, 0.0)

    def _get_float_state(self, entity_id: str, default: float) -> float:
        """Extract float value safely from Home Assistant state machine."""
        if not entity_id:
            return default
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable"):
            return default
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return default

    def _get_bool_state(self, entity_id: str, default: bool) -> bool:
        """Extract binary state safely from Home Assistant state machine."""
        if not entity_id:
            return default
        state = self.hass.states.get(entity_id)
        if state is None or state.state in ("unknown", "unavailable"):
            return default
        return state.state.lower() in ("on", "true", "1")

    @callback
    def _async_handle_state_change(self, event: Event) -> None:
        """Handle state change event for tracked sensors."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        mandatory = (self.sensor_t_in, self.sensor_t_out, self.sensor_ac_power)
        if entity_id in mandatory:
            if new_state is None or new_state.state in ("unknown", "unavailable"):
                if entity_id not in self._unavailable_mandatory_sensors:
                    self._unavailable_mandatory_sensors.add(entity_id)
                    _LOGGER.warning(
                        "Mandatory sensor %s became unavailable (state: %s)",
                        entity_id,
                        getattr(new_state, "state", None),
                    )
                self.last_update_success = False
                self.async_update_listeners()
                return

            if entity_id in self._unavailable_mandatory_sensors:
                self._unavailable_mandatory_sensors.remove(entity_id)
                _LOGGER.info(
                    "Mandatory sensor %s recovered and is now available (state: %s)",
                    entity_id,
                    new_state.state,
                )
                if not self._unavailable_mandatory_sensors:
                    self.last_update_success = True

        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return

        if entity_id == self.sensor_t_in:
            self.t_in_val = _safe_float(new_state.state, self.t_in_val)
        elif entity_id == self.sensor_t_out:
            self.t_out_val = _safe_float(new_state.state, self.t_out_val)
        elif entity_id == self.sensor_t_ac_exit:
            self.t_ac_exit_val = _safe_float(new_state.state, self.t_ac_exit_val)
        elif entity_id == self.sensor_rh_in:
            self.rh_in_val = _safe_float(new_state.state, self.rh_in_val)
        elif entity_id == self.sensor_rh_out:
            self.rh_out_val = _safe_float(new_state.state, self.rh_out_val)
        elif entity_id == self.sensor_solar:
            self.solar_val = _safe_float(new_state.state, self.solar_val)
        elif entity_id == self.sensor_ac_power:
            self.ac_power_val = _safe_float(new_state.state, self.ac_power_val)
        elif entity_id == self.sensor_window:
            self.window_is_open = new_state.state.lower() in ("on", "true", "1")
        elif entity_id == self.sensor_illuminance:
            self.illuminance_val = _safe_float(new_state.state, self.illuminance_val)
            self.curtains_closed = (self.illuminance_val < self.illuminance_threshold)
        elif entity_id == self.sensor_wind_speed:
            val = _safe_float(new_state.state, 0.0)
            unit = new_state.attributes.get("unit_of_measurement")
            self.wind_speed_ms = normalize_wind_speed(val, unit)
        elif entity_id == self.sensor_wind_direction:
            self.wind_dir_deg = _safe_float(new_state.state, self.wind_dir_deg)

        self.recalculate()

    @callback
    def _async_handle_periodic_update(self, now: datetime) -> None:
        """Periodically recalculate energy accumulators and states every 30 seconds."""
        self.recalculate()

    @callback
    def _async_handle_midnight_reset(self, now: datetime) -> None:
        """Reset daily energy accumulators at 00:00."""
        _LOGGER.info("Resetting daily thermal balance accumulators at midnight")
        self.engine.accumulator.reset_daily(now)
        self.recalculate()

    def recalculate(self) -> None:
        """Perform central calculation delegating domain work to ThermalEngine."""
        now = dt_util.now()

        # Window state check
        if self.has_window_sensor:
            self.window_is_open = self._get_bool_state(self.sensor_window, False)
        else:
            self.window_is_open = False

        # Daylight and Solar Position
        is_sun_above_horizon = False
        sun_elevation = 0.0
        sun_azimuth = 180.0
        has_sun_position = False
        sun_state = self.hass.states.get("sun.sun")
        if sun_state is not None:
            sun_elevation = _safe_float(sun_state.attributes.get("elevation"), 0.0)
            sun_azimuth = _safe_float(sun_state.attributes.get("azimuth"), 180.0)
            has_sun_position = True
            if sun_state.state == "above_horizon" or sun_elevation > 0.0:
                is_sun_above_horizon = True

        # Solar Irradiance: physical sensor OR clear-sky + weather cloud cover model
        cloud_coverage_pct = 0.0
        if self.has_weather_sensor:
            w_state = self.hass.states.get(self.sensor_weather)
            if w_state is not None and w_state.state not in ("unknown", "unavailable"):
                cloud_coverage_pct = parse_cloud_coverage(str(w_state.state), w_state.attributes)

        if not self.has_solar_sensor:
            self.solar_val = estimate_solar_irradiance(sun_elevation, cloud_coverage_pct)
        else:
            s_state = self.hass.states.get(self.sensor_solar)
            if s_state is not None and s_state.state not in ("unknown", "unavailable"):
                try:
                    self.solar_val = max(0.0, float(s_state.state))
                except (ValueError, TypeError):
                    self.solar_val = estimate_solar_irradiance(sun_elevation, cloud_coverage_pct)
            else:
                self.solar_val = estimate_solar_irradiance(sun_elevation, cloud_coverage_pct)

        is_daylight = (self.solar_val > 10.0) or is_sun_above_horizon
        self.curtains_closed, self.curtains_note = resolve_curtains_closed(
            self.illuminance_val,
            self.illuminance_threshold,
            self.has_illuminance_sensor,
            is_daylight,
        )

        # Determine active heating vs cooling state
        climate_state = None
        climate_action = None
        if self.sensor_climate:
            c_state = self.hass.states.get(self.sensor_climate)
            if c_state is not None and c_state.state not in ("unknown", "unavailable"):
                climate_state = str(c_state.state)
                climate_action = str(c_state.attributes.get("hvac_action", ""))

        self.is_heating = resolve_is_heating(
            self.hvac_mode,
            climate_state,
            climate_action,
            self.t_out_val,
            self.t_in_val,
        )

        # Delegate full cycle computation to domain ThermalEngine
        cycle_inputs = EngineCycleInputs(
            now=now,
            t_in=self.t_in_val,
            t_out=self.t_out_val,
            t_ac_exit=self.t_ac_exit_val,
            rh_in=self.rh_in_val,
            rh_out=self.rh_out_val,
            solar_irradiance=self.solar_val,
            ac_power=self.ac_power_val,
            window_is_open=self.window_is_open,
            curtains_closed=self.curtains_closed,
            curtains_note=self.curtains_note,
            curtain_type=self.curtain_type,
            wind_speed_ms=self.wind_speed_ms,
            wind_dir_deg=self.wind_dir_deg,
            window_azimuth=self.window_azimuth,
            sun_elevation_deg=sun_elevation,
            sun_azimuth_deg=sun_azimuth,
            has_sun_position=has_sun_position,
            is_heating=self.is_heating,
            hvac_mode=self.hvac_mode,
            illuminance_lux=self.illuminance_val if self.has_illuminance_sensor else None,
            has_window_sensor=self.has_window_sensor,
            has_illuminance_sensor=self.has_illuminance_sensor,
            has_wind_speed_sensor=self.has_wind_speed_sensor,
            has_wind_dir_sensor=self.has_wind_dir_sensor,
            has_t_ac_exit_sensor=self.has_t_ac_exit_sensor,
            has_rh_in_sensor=self.has_rh_in_sensor,
            has_rh_out_sensor=self.has_rh_out_sensor,
            electricity_rate=self.electricity_rate,
            use_empirical_hlc=self.use_empirical_hlc,
            ac_max_cooling=self.ac_max_cooling,
            ac_airflow=self.ac_airflow,
        )

        cycle_output = self.engine.process_cycle(cycle_inputs)

        self.dt_dt_c_per_h = cycle_output.dt_dt_c_per_h
        self.p_storage_w = self.engine.calibrator.p_storage_w
        self.p_wall_dynamic_w = self.engine.calibrator.p_wall_dynamic_w
        self.data = cycle_output.data
        self.extra_attributes = cycle_output.extra_attributes

        # Notify all CoordinatorEntity instances
        if self._unavailable_mandatory_sensors:
            self.last_update_success = False
            self.async_update_listeners()
        else:
            self.async_set_updated_data(self.data)
