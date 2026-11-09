"""Pure domain thermal balance calculations, time-series history, calibration, and energy tracking."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import math
from typing import Any

from .const import (
    BINARY_SENSOR_INSUFFICIENT_COOLING_CAPACITY,
    BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS,
    BINARY_SENSOR_RECOMMEND_OPEN_WINDOW,
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
from .model import (
    CURTAIN_TYPE_FACTORS,
    RoomGeometry,
    ThermalCalculationResult,
    ThermodynamicInputs,
    calculate_ac_performance,
    calculate_dynamic_k_factor,
    calculate_solar_radiation,
    calculate_thermal_balance,
)

_LOGGER = logging.getLogger(__name__)


def parse_cloud_coverage(
    weather_state: str | None,
    weather_attributes: dict[str, Any] | None = None,
) -> float:
    """Parse cloud coverage percentage from weather entity state and attributes."""
    if weather_attributes and "cloud_coverage" in weather_attributes:
        try:
            return float(weather_attributes["cloud_coverage"])
        except (ValueError, TypeError):
            pass

    if not weather_state or weather_state in ("unknown", "unavailable"):
        return 0.0

    cond = weather_state.lower().strip()
    if cond in ("sunny", "clear-night", "clear"):
        return 0.0
    if cond in ("partlycloudy", "windy", "windy-variant"):
        return 40.0
    if cond in ("cloudy", "fog"):
        return 80.0
    if cond in ("rainy", "pouring", "lightning", "lightning-rainy", "snowy", "snowy-rainy", "hail"):
        return 95.0

    return 0.0


def normalize_wind_speed(raw_speed: float, unit_of_measurement: str | None) -> float:
    """Normalize wind speed to meters per second (m/s)."""
    if unit_of_measurement and unit_of_measurement.lower() in ("km/h", "kmh"):
        return raw_speed / 3.6
    return max(0.0, raw_speed)


def resolve_is_heating(
    hvac_mode: str,
    climate_state: str | None,
    climate_action: str | None,
    t_out: float,
    t_in: float,
) -> bool:
    """Determine whether HVAC system is in heating or cooling mode."""
    if hvac_mode == HVAC_MODE_HEATING:
        return True
    if hvac_mode == HVAC_MODE_COOLING:
        return False

    # HVAC_MODE_AUTO
    if climate_action:
        action = climate_action.lower().strip()
        if action in ("heating", "heat"):
            return True
        if action in ("cooling", "cool"):
            return False

    if climate_state and climate_state not in ("unknown", "unavailable"):
        state = climate_state.lower().strip()
        if state in ("heat", "heating"):
            return True
        if state in ("cool", "cooling"):
            return False

    return bool(t_out < 16.0 and t_out < t_in)


def resolve_curtains_closed(
    illuminance_lux: float,
    illuminance_threshold: float,
    has_illuminance_sensor: bool,
    is_daylight: bool,
) -> tuple[bool, str | None]:
    """Determine curtain closure state and explanation note based on daylight and illuminance."""
    if not has_illuminance_sensor:
        return False, "Illuminance sensor not configured"

    if not is_daylight:
        return False, "Night: auto curtain detection disabled (lux threshold not applied)"

    is_closed = illuminance_lux < illuminance_threshold
    return is_closed, None


class ThermalHistoryTracker:
    """Tracks indoor temperature history and calculates dT/dt derivative using rolling linear regression."""

    def __init__(self, maxlen: int = 60, window_minutes: int = 10) -> None:
        """Initialize the history tracker."""
        self._history: deque[tuple[datetime, float]] = deque(maxlen=maxlen)
        self.window_minutes = window_minutes

    @property
    def history(self) -> deque[tuple[datetime, float]]:
        """Return the temperature history buffer."""
        return self._history

    def reset(self) -> None:
        """Clear all historical readings."""
        self._history.clear()

    def update(self, now: datetime, t_in: float) -> float:
        """Append indoor temperature reading and return rate of change dT/dt in °C/hour."""
        if not self._history:
            self._history.append((now, t_in))
        else:
            last_t, last_temp = self._history[-1]
            elapsed_sec = (now - last_t).total_seconds()
            temp_delta = abs(t_in - last_temp)

            if elapsed_sec >= 20.0 or temp_delta >= 0.02:
                if elapsed_sec < 5.0:
                    self._history[-1] = (now, t_in)
                else:
                    self._history.append((now, t_in))

        # Filter out readings older than the time window
        cutoff = now - timedelta(minutes=self.window_minutes)
        while self._history and self._history[0][0] < cutoff:
            self._history.popleft()

        # Need at least 3 points spanning at least 45 seconds for meaningful slope
        if len(self._history) < 3:
            return 0.0

        t0 = self._history[0][0]
        t_span = (self._history[-1][0] - t0).total_seconds()
        if t_span < 45.0:
            return 0.0

        # Linear regression slope in °C per hour
        times_h = [(t - t0).total_seconds() / 3600.0 for t, _ in self._history]
        temps = [temp for _, temp in self._history]

        n = len(times_h)
        mean_t = sum(times_h) / n
        mean_temp = sum(temps) / n

        denom = sum((t - mean_t) ** 2 for t in times_h)
        if denom <= 1e-7:
            return 0.0

        numer = sum((times_h[i] - mean_t) * (temps[i] - mean_temp) for i in range(n))
        slope = numer / denom

        # Clamp slope to realistic building thermodynamic bounds (-10°C/h to +10°C/h)
        return max(-10.0, min(10.0, slope))


class InsulationCalibrator:
    """Continuous-time EMA estimator for building Heat Loss Coefficient (empirical K-factor)."""

    def __init__(self, initial_hlc: float) -> None:
        """Initialize the calibrator."""
        self.empirical_k_val: float = initial_hlc
        self.samples_count: int = 0
        self.hlc_closed: float = initial_hlc
        self.last_calibration_time: datetime | None = None
        self.p_storage_w: float = 0.0
        self.p_wall_dynamic_w: float = 0.0

    def reset(self, initial_hlc: float) -> None:
        """Reset calibration state."""
        self.empirical_k_val = initial_hlc
        self.samples_count = 0
        self.hlc_closed = initial_hlc
        self.last_calibration_time = None
        self.p_storage_w = 0.0
        self.p_wall_dynamic_w = 0.0

    def calibrate(
        self,
        now: datetime,
        geometry: RoomGeometry,
        inputs: ThermodynamicInputs,
        dt_dt_c_per_h: float,
        ac_max_cooling: float,
        ac_airflow: float,
        use_empirical_hlc: bool,
    ) -> float:
        """Run dynamic K-factor estimation and return active HLC."""
        if not inputs.window_is_open and inputs.ac_power >= 50.0:
            curtain_factors = CURTAIN_TYPE_FACTORS.get(inputs.curtain_type, CURTAIN_TYPE_FACTORS["roller_gaps"])
            curtain_g = curtain_factors[0] if inputs.curtains_closed else 0.70
            p_sol, *_ = calculate_solar_radiation(
                window_area=geometry.window_area,
                solar_irradiance=max(0.0, inputs.solar_irradiance),
                curtain_g_factor=curtain_g,
                window_azimuth=inputs.window_azimuth,
                sun_elevation_deg=inputs.sun_elevation_deg,
                sun_azimuth_deg=inputs.sun_azimuth_deg,
                has_sun_position=inputs.has_sun_position,
            )
            ac_perf_pre = calculate_ac_performance(inputs, ac_max_cooling, ac_airflow)
            p_hvac = ac_perf_pre.p_heating if inputs.is_heating else ac_perf_pre.p_cooling_sensible

            k_instant, p_storage, p_wall_dyn = calculate_dynamic_k_factor(
                t_in=inputs.t_in,
                t_out=inputs.t_out,
                p_hvac=p_hvac,
                p_solar=p_sol,
                c_total=geometry.c_total,
                dt_dt_c_per_h=dt_dt_c_per_h,
                hlc_theoretical=geometry.hlc_theoretical,
                is_heating=inputs.is_heating,
            )
            self.p_storage_w = p_storage
            self.p_wall_dynamic_w = p_wall_dyn

            if k_instant is not None:
                delta_cal_sec = (
                    (now - self.last_calibration_time).total_seconds()
                    if self.last_calibration_time
                    else 30.0
                )
                if delta_cal_sec >= 15.0:
                    tau = 300.0 if self.samples_count < 30 else 900.0
                    alpha = 1.0 - math.exp(-min(delta_cal_sec, 300.0) / tau)
                    self.empirical_k_val = (1.0 - alpha) * self.empirical_k_val + alpha * k_instant
                    self.samples_count += 1
                    self.last_calibration_time = now
        else:
            self.p_storage_w = geometry.c_total * dt_dt_c_per_h
            self.p_wall_dynamic_w = 0.0

        self.empirical_k_val = max(
            0.5 * geometry.hlc_theoretical,
            min(2.0 * geometry.hlc_theoretical, self.empirical_k_val),
        )

        if use_empirical_hlc and self.samples_count >= 5:
            self.hlc_closed = self.empirical_k_val
        else:
            self.hlc_closed = geometry.hlc_theoretical

        return self.hlc_closed

    def get_grade(self, hlc_theoretical: float) -> tuple[str, float]:
        """Return human-readable insulation grade and deviation percentage."""
        dev_pct = (
            (self.empirical_k_val - hlc_theoretical)
            / max(0.1, hlc_theoretical)
        ) * 100.0

        if dev_pct <= 15.0:
            grade = "Excellent (passport)"
        elif dev_pct <= 35.0:
            grade = "Good (moderate)"
        elif dev_pct <= 65.0:
            grade = "Average (thermal bridges)"
        else:
            grade = "Poor (drafts)"

        return grade, dev_pct


class EnergyAccumulator:
    """Manages bounded numerical Riemann integration for thermal and electrical energy."""

    def __init__(self) -> None:
        """Initialize accumulators."""
        self.total_heat_absorbed: float = 0.0
        self.ac_thermal_energy_total: float = 0.0
        self.daily_heat_absorbed: float = 0.0
        self.daily_ac_thermal_energy: float = 0.0
        self.daily_ac_elec_kwh: float = 0.0
        self.daily_shading_heat_saved_kwh: float = 0.0
        self.last_update_time: datetime | None = None
        self.last_daily_reset: datetime | None = None

    def check_daily_boundary(self, now: datetime) -> bool:
        """Check if date has rolled over and reset daily counters if so."""
        if self.last_daily_reset is not None and now.date() != self.last_daily_reset.date():
            self.reset_daily(now)
            return True
        self.last_daily_reset = now
        return False

    def reset_daily(self, now: datetime | None = None) -> None:
        """Reset daily counters."""
        self.daily_heat_absorbed = 0.0
        self.daily_ac_thermal_energy = 0.0
        self.daily_ac_elec_kwh = 0.0
        self.daily_shading_heat_saved_kwh = 0.0
        if now:
            self.last_daily_reset = now

    def reset_all(self, now: datetime | None = None) -> None:
        """Reset all accumulators (both all-time and daily)."""
        self.total_heat_absorbed = 0.0
        self.ac_thermal_energy_total = 0.0
        self.reset_daily(now)

    def integrate_step(
        self,
        now: datetime,
        p_gain: float,
        p_hvac_output: float,
        ac_power: float,
        p_solar: float,
        curtain_g_factor: float,
        curtain_saved_fraction: float,
        curtains_closed: bool,
    ) -> None:
        """Perform a single bounded Riemann integration step (max 60 seconds)."""
        if self.last_update_time is not None:
            delta_sec = (now - self.last_update_time).total_seconds()
            if delta_sec > 0:
                clamped_sec = min(delta_sec, 60.0)
                delta_hours = clamped_sec / 3600.0

                p_heat_absorbed_w = max(0.0, p_gain)
                e_heat_new = (p_heat_absorbed_w * delta_hours) / 1000.0
                e_hvac_new = (p_hvac_output * delta_hours) / 1000.0
                e_ac_elec_new = (ac_power * delta_hours) / 1000.0

                incident_solar_w = (
                    (p_solar / max(0.01, curtain_g_factor))
                    if curtain_g_factor > 0
                    else 0.0
                )
                p_solar_saved = (incident_solar_w * curtain_saved_fraction) if curtains_closed else 0.0
                e_shading_saved_new = (p_solar_saved * delta_hours) / 1000.0

                self.total_heat_absorbed += e_heat_new
                self.ac_thermal_energy_total += e_hvac_new
                self.daily_heat_absorbed += e_heat_new
                self.daily_ac_thermal_energy += e_hvac_new
                self.daily_ac_elec_kwh += e_ac_elec_new
                self.daily_shading_heat_saved_kwh += e_shading_saved_new

        self.last_update_time = now

    def calculate_financials(
        self,
        electricity_rate: float,
        cop: float,
    ) -> tuple[float, float]:
        """Calculate AC electricity cost and shading monetary savings."""
        ac_energy_cost = self.daily_ac_elec_kwh * electricity_rate
        cop_for_calc = cop if cop > 0 else 3.2
        shading_saved_elec_kwh = self.daily_shading_heat_saved_kwh / max(1.0, cop_for_calc)
        shading_daily_savings = shading_saved_elec_kwh * electricity_rate
        return ac_energy_cost, shading_daily_savings


class ClimateAdvisor:
    """Evaluates rule-based smart recommendations for natural cooling and shading."""

    @staticmethod
    def evaluate(
        t_in: float,
        t_out: float,
        window_is_open: bool,
        is_heating: bool,
        is_daylight: bool,
        p_solar_direct: float,
        p_solar: float,
        solar_val: float,
        sun_is_direct: bool,
        curtains_closed: bool,
    ) -> tuple[bool, bool]:
        """Evaluate open window and close curtains recommendations."""
        rec_open_window = bool(
            (t_out < t_in - 1.0)
            and (t_in >= 22.0)
            and not window_is_open
            and not is_heating
        )

        rec_close_curtains = bool(
            is_daylight
            and (
                (p_solar_direct > 50.0)
                or (p_solar > 100.0)
                or (solar_val >= 200.0 and sun_is_direct)
            )
            and not curtains_closed
            and not is_heating
        )

        return rec_open_window, rec_close_curtains


@dataclass
class EngineCycleInputs:
    """Aggregated cycle inputs for ThermalEngine."""

    now: datetime
    t_in: float
    t_out: float
    t_ac_exit: float | None
    rh_in: float
    rh_out: float
    solar_irradiance: float
    ac_power: float
    window_is_open: bool
    curtains_closed: bool
    curtains_note: str | None
    curtain_type: str
    wind_speed_ms: float
    wind_dir_deg: float
    window_azimuth: float
    sun_elevation_deg: float
    sun_azimuth_deg: float
    has_sun_position: bool
    is_heating: bool
    hvac_mode: str
    illuminance_lux: float | None
    has_window_sensor: bool
    has_illuminance_sensor: bool
    has_wind_speed_sensor: bool
    has_wind_dir_sensor: bool
    has_t_ac_exit_sensor: bool
    has_rh_in_sensor: bool
    has_rh_out_sensor: bool
    electricity_rate: float
    use_empirical_hlc: bool
    ac_max_cooling: float
    ac_airflow: float


@dataclass
class EngineCycleOutput:
    """Aggregated output from a cycle calculation."""

    data: dict[str, Any]
    extra_attributes: dict[str, dict[str, Any]]
    result: ThermalCalculationResult
    dt_dt_c_per_h: float
    insulation_grade: str
    dev_pct: float


class ThermalEngine:
    """Core domain coordinator orchestrating history, calibration, physics, accumulators, and advice."""

    def __init__(self, geometry: RoomGeometry) -> None:
        """Initialize the thermal engine."""
        self.geometry = geometry
        self.history_tracker = ThermalHistoryTracker()
        self.calibrator = InsulationCalibrator(geometry.hlc_theoretical)
        self.accumulator = EnergyAccumulator()
        self.advisor = ClimateAdvisor()

    def process_cycle(self, inputs: EngineCycleInputs) -> EngineCycleOutput:
        """Execute a full thermodynamic evaluation and update state."""
        now = inputs.now

        # 1. Date boundary check
        self.accumulator.check_daily_boundary(now)

        # 2. Temperature derivative dT/dt estimation
        dt_dt_c_per_h = self.history_tracker.update(now, inputs.t_in)

        # 3. Build model inputs
        model_inputs = ThermodynamicInputs(
            t_in=inputs.t_in,
            t_out=inputs.t_out,
            solar_irradiance=inputs.solar_irradiance,
            ac_power=inputs.ac_power,
            t_ac_exit=inputs.t_ac_exit if inputs.has_t_ac_exit_sensor else None,
            rh_in=inputs.rh_in,
            rh_out=inputs.rh_out,
            window_is_open=inputs.window_is_open,
            curtains_closed=inputs.curtains_closed,
            curtain_type=inputs.curtain_type,
            wind_speed_ms=inputs.wind_speed_ms,
            wind_dir_deg=inputs.wind_dir_deg,
            window_azimuth=inputs.window_azimuth,
            sun_elevation_deg=inputs.sun_elevation_deg,
            sun_azimuth_deg=inputs.sun_azimuth_deg,
            is_heating=inputs.is_heating,
            hvac_mode=inputs.hvac_mode,
            has_rh_in=inputs.has_rh_in_sensor,
            has_rh_out=inputs.has_rh_out_sensor,
            has_t_ac_exit=inputs.has_t_ac_exit_sensor,
            has_wind_speed=inputs.has_wind_speed_sensor,
            has_wind_dir=inputs.has_wind_dir_sensor,
            has_sun_position=inputs.has_sun_position,
        )

        # 4. Calibration of Heat Loss Coefficient (empirical K-factor)
        hlc_closed = self.calibrator.calibrate(
            now=now,
            geometry=self.geometry,
            inputs=model_inputs,
            dt_dt_c_per_h=dt_dt_c_per_h,
            ac_max_cooling=inputs.ac_max_cooling,
            ac_airflow=inputs.ac_airflow,
            use_empirical_hlc=inputs.use_empirical_hlc,
        )

        grade, dev_pct = self.calibrator.get_grade(self.geometry.hlc_theoretical)

        # 5. Core thermodynamic physics calculation
        result: ThermalCalculationResult = calculate_thermal_balance(
            self.geometry,
            model_inputs,
            inputs.ac_max_cooling,
            inputs.ac_airflow,
            hlc_closed,
        )

        # 6. Energy accumulators integration
        self.accumulator.integrate_step(
            now=now,
            p_gain=result.p_gain,
            p_hvac_output=result.p_hvac_output,
            ac_power=inputs.ac_power,
            p_solar=result.p_solar,
            curtain_g_factor=result.curtain_g_factor,
            curtain_saved_fraction=result.curtain_saved_fraction,
            curtains_closed=inputs.curtains_closed,
        )

        daily_balance = self.accumulator.daily_heat_absorbed - self.accumulator.daily_ac_thermal_energy
        net_balance = self.accumulator.total_heat_absorbed - self.accumulator.ac_thermal_energy_total

        # 7. Financial calculations
        ac_energy_cost, shading_daily_savings = self.accumulator.calculate_financials(
            electricity_rate=inputs.electricity_rate,
            cop=result.cop,
        )

        # 8. Smart advice & recommendations
        is_daylight = (inputs.solar_irradiance > 10.0) or (inputs.sun_elevation_deg > 0.0)
        rec_open_window, rec_close_curtains = self.advisor.evaluate(
            t_in=inputs.t_in,
            t_out=inputs.t_out,
            window_is_open=inputs.window_is_open,
            is_heating=inputs.is_heating,
            is_daylight=is_daylight,
            p_solar_direct=result.p_solar_direct,
            p_solar=result.p_solar,
            solar_val=inputs.solar_irradiance,
            sun_is_direct=result.sun_is_direct,
            curtains_closed=inputs.curtains_closed,
        )

        # 9. Format sensor state dictionary
        data: dict[str, Any] = {
            SENSOR_INSTANT_HEAT_GAIN: round(result.p_gain, 2),
            SENSOR_AC_HEAT_OUTPUT: round(result.p_hvac_output, 2),
            SENSOR_INSTANT_NET_BALANCE: round(result.p_net, 2),
            SENSOR_AC_CARNOT_COP: round(result.cop, 2),
            SENSOR_TIME_TO_1DEG: round(result.time_to_1deg_min, 1),
            SENSOR_DAILY_THERMAL_BALANCE: round(daily_balance, 3),
            SENSOR_NET_THERMAL_BALANCE: round(net_balance, 3),
            SENSOR_TOTAL_HEAT_ABSORBED: round(self.accumulator.total_heat_absorbed, 3),
            SENSOR_AC_THERMAL_ENERGY_TOTAL: round(self.accumulator.ac_thermal_energy_total, 3),
            SENSOR_AC_CONDENSATION_RATE: round(result.condensation_rate_lh, 2),
            SENSOR_EMPIRICAL_K_FACTOR: round(self.calibrator.empirical_k_val, 2),
            SENSOR_EQUILIBRIUM_TEMPERATURE: round(result.t_equilibrium, 1),
            SENSOR_REQUIRED_AC_POWER: round(result.p_required_hvac, 0),
            SENSOR_AC_ENERGY_COST: round(ac_energy_cost, 2),
            SENSOR_SHADING_DAILY_SAVINGS: round(shading_daily_savings, 2),
            BINARY_SENSOR_RECOMMEND_OPEN_WINDOW: rec_open_window,
            BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS: rec_close_curtains,
            BINARY_SENSOR_INSUFFICIENT_COOLING_CAPACITY: bool(result.is_capacity_insufficient),
        }

        # 10. Format entity extra attributes
        window_mode = "sensor" if inputs.has_window_sensor else "no_sensor"
        curtains_state = "Closed" if inputs.curtains_closed else "Open"

        extra_attributes: dict[str, dict[str, Any]] = {
            SENSOR_INSTANT_HEAT_GAIN: {
                "p_solar_w": round(result.p_solar, 1),
                "p_solar_direct_w": round(result.p_solar_direct, 1),
                "p_solar_diffuse_w": round(result.p_solar_diffuse, 1),
                "solar_aoi_deg": round(result.solar_aoi_deg, 1) if result.solar_aoi_deg is not None else None,
                "solar_cos_aoi": round(result.solar_cos_aoi, 3),
                "sun_is_direct_to_window": result.sun_is_direct,
                "sun_elevation_deg": round(inputs.sun_elevation_deg, 1) if inputs.has_sun_position else None,
                "sun_azimuth_deg": round(inputs.sun_azimuth_deg, 1) if inputs.has_sun_position else None,
                "p_wall_w": round(result.p_wall, 1),
                "p_trans_w": round(result.p_trans, 1),
                "p_vent_w": round(result.p_vent, 1),
                "p_env_w": round(result.p_env, 1),
                "p_gain_w": round(result.p_gain, 1),
                "p_loss_w": round(result.p_loss, 1),
                "hlc_w_k": round(result.hlc_total, 2),
                "window_is_open": inputs.window_is_open,
                "window_mode": window_mode,
                "curtains_closed": inputs.curtains_closed,
                "curtains_state": curtains_state,
                "curtains_note": inputs.curtains_note,
                "curtain_type": inputs.curtain_type,
                "curtain_saved_percent": int(round(result.curtain_saved_fraction * 100)),
                "curtain_glass_reduce_percent": int(round((0.70 - result.curtain_g_factor) / 0.70 * 100)),
                "illuminance_lux": round(inputs.illuminance_lux, 1) if inputs.illuminance_lux is not None else None,
                "g_solar_factor": result.curtain_g_factor,
                "wind_speed_ms": round(inputs.wind_speed_ms, 2) if inputs.has_wind_speed_sensor else None,
                "wind_dir_deg": round(inputs.wind_dir_deg, 1) if inputs.has_wind_dir_sensor else None,
                "window_azimuth": round(inputs.window_azimuth, 1),
                "ventilation_ach": round(result.ventilation_ach, 2),
                "recommend_open_window": rec_open_window,
                "recommend_close_curtains": rec_close_curtains,
            },
            SENSOR_INSTANT_NET_BALANCE: {
                "p_env_w": round(result.p_env, 1),
                "p_cooling_w": round(result.p_cooling, 1),
                "p_heating_w": round(result.p_heating, 1),
                "p_hvac_output_w": round(result.p_hvac_output, 1),
                "p_wall_w": round(result.p_wall, 1),
                "p_vent_w": round(result.p_vent, 1),
                "hlc_w_k": round(result.hlc_total, 2),
                "window_is_open": inputs.window_is_open,
                "is_heating": inputs.is_heating,
                "hvac_mode": inputs.hvac_mode,
            },
            SENSOR_TIME_TO_1DEG: {
                "direction": result.direction,
                "direction_text": result.direction_text,
            },
            SENSOR_AC_HEAT_OUTPUT: {
                "is_heating": inputs.is_heating,
                "hvac_mode": inputs.hvac_mode,
                "mode": "heating" if inputs.is_heating else "cooling",
                "p_heating_w": round(result.p_heating, 1),
                "p_cooling_w": round(result.p_cooling, 1),
                "delta_t_ac_c": round(result.ac_performance.delta_t_ac, 1),
                "ac_exit_temperature_c": round(result.ac_performance.t_ac_exit, 1),
                "ac_calc_exit_temperature_c": round(result.ac_performance.t_ac_exit_calc, 1),
                "sensible_cooling_w": round(result.p_cooling_sensible, 1),
                "latent_cooling_w": round(result.p_cooling_latent, 1),
                "shr_percent": round(result.ac_performance.shr * 100, 1),
                "indoor_dew_point_c": round(result.ac_performance.dew_point_in, 1) if result.ac_performance.dew_point_in is not None else None,
                "outdoor_dew_point_c": round(result.ac_performance.dew_point_out, 1) if result.ac_performance.dew_point_out is not None else None,
                "air_enthalpy_in_kj_kg": round(result.ac_performance.enthalpy_in_kj_kg, 2),
                "ac_airflow_m3h": round(inputs.ac_airflow, 1),
                "has_measured_exit_sensor": inputs.has_t_ac_exit_sensor,
            },
            SENSOR_DAILY_THERMAL_BALANCE: {
                "daily_heat_absorbed": round(self.accumulator.daily_heat_absorbed, 3),
                "daily_ac_thermal_energy": round(self.accumulator.daily_ac_thermal_energy, 3),
                "daily_ac_elec_kwh": round(self.accumulator.daily_ac_elec_kwh, 3),
                "daily_shading_heat_saved_kwh": round(self.accumulator.daily_shading_heat_saved_kwh, 3),
            },
            SENSOR_NET_THERMAL_BALANCE: {
                "total_heat_absorbed": round(self.accumulator.total_heat_absorbed, 3),
                "ac_thermal_energy_total": round(self.accumulator.ac_thermal_energy_total, 3),
            },
            SENSOR_EMPIRICAL_K_FACTOR: {
                "theoretical_hlc_w_k": round(self.geometry.hlc_theoretical, 2),
                "active_hlc_w_k": round(hlc_closed, 2),
                "deviation_percent": round(dev_pct, 1),
                "insulation_grade": grade,
                "auto_calibrated": inputs.use_empirical_hlc and self.calibrator.samples_count >= 5,
                "samples_count": self.calibrator.samples_count,
                "dt_dt_c_per_h": round(dt_dt_c_per_h, 3),
                "p_storage_w": round(self.calibrator.p_storage_w, 1),
                "p_wall_dynamic_w": round(self.calibrator.p_wall_dynamic_w, 1),
            },
        }

        return EngineCycleOutput(
            data=data,
            extra_attributes=extra_attributes,
            result=result,
            dt_dt_c_per_h=dt_dt_c_per_h,
            insulation_grade=grade,
            dev_pct=dev_pct,
        )
