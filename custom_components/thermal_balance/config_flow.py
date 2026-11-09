"""Config flow for Thermal Balance integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
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
    DOMAIN,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOLING,
    HVAC_MODE_HEATING,
)


def _safe_float(val: Any, default: float) -> float:
    """Safely convert value to float."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def get_geometry_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Return Step 1: Room Geometry & Architecture schema."""
    ext_walls_default = str(_safe_float(defaults.get(CONF_EXTERNAL_WALLS_FRACTION), DEFAULT_EXTERNAL_WALLS_FRACTION))
    if ext_walls_default not in ("0.25", "0.5", "0.50", "0.75", "1.0", "1.00"):
        ext_walls_default = "0.25"
    if ext_walls_default == "0.5":
        ext_walls_default = "0.50"
    if ext_walls_default == "1.0":
        ext_walls_default = "1.00"

    schema_dict: dict[Any, Any] = {
        vol.Required(
            CONF_ROOM_AREA,
            default=_safe_float(defaults.get(CONF_ROOM_AREA), DEFAULT_ROOM_AREA),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1.0, max=500.0, step=0.1, unit_of_measurement="m²", mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Required(
            CONF_CEILING_HEIGHT,
            default=_safe_float(defaults.get(CONF_CEILING_HEIGHT), DEFAULT_CEILING_HEIGHT),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1.0, max=20.0, step=0.1, unit_of_measurement="m", mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Required(
            CONF_WINDOW_AREA,
            default=_safe_float(defaults.get(CONF_WINDOW_AREA), DEFAULT_WINDOW_AREA),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.0, max=100.0, step=0.1, unit_of_measurement="m²", mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Required(
            CONF_EXTERNAL_WALLS_FRACTION,
            default=ext_walls_default,
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(value="0.25", label="0.25 (1 of 4 walls — typical room)"),
                    selector.SelectOptionDict(value="0.50", label="0.50 (2 of 4 walls — corner room)"),
                    selector.SelectOptionDict(value="0.75", label="0.75 (3 of 4 walls)"),
                    selector.SelectOptionDict(value="1.00", label="1.00 (4 walls — detached house)"),
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(
            CONF_WINDOW_AZIMUTH,
            default=_safe_float(defaults.get(CONF_WINDOW_AZIMUTH), DEFAULT_WINDOW_AZIMUTH),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.0, max=359.9, step=1.0, unit_of_measurement="°", mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Required(
            CONF_U_WALL,
            default=_safe_float(defaults.get(CONF_U_WALL), DEFAULT_U_WALL),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.01, max=10.0, step=0.01, unit_of_measurement="W/(m²·K)", mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Required(
            CONF_U_WINDOW,
            default=_safe_float(defaults.get(CONF_U_WINDOW), DEFAULT_U_WINDOW),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.1, max=10.0, step=0.01, unit_of_measurement="W/(m²·K)", mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Optional(
            CONF_USE_EMPIRICAL_HLC,
            default=bool(defaults.get(CONF_USE_EMPIRICAL_HLC, DEFAULT_USE_EMPIRICAL_HLC)),
        ): selector.BooleanSelector(),
    }
    return vol.Schema(schema_dict)


def get_equipment_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Return Step 2: AC Performance, Shading & Financial schema."""
    hvac_mode_val = str(defaults.get(CONF_HVAC_MODE, DEFAULT_HVAC_MODE))
    if hvac_mode_val not in (HVAC_MODE_COOLING, HVAC_MODE_HEATING, HVAC_MODE_AUTO):
        hvac_mode_val = DEFAULT_HVAC_MODE

    curtain_type_val = str(defaults.get(CONF_CURTAIN_TYPE, DEFAULT_CURTAIN_TYPE))
    if curtain_type_val not in ("roller_gaps", "blackout", "standard", "blinds", "external"):
        curtain_type_val = "roller_gaps"

    vol_rate = _safe_float(defaults.get(CONF_ELECTRICITY_RATE), DEFAULT_ELECTRICITY_RATE)
    curr_sym = str(defaults.get(CONF_CURRENCY_SYMBOL, ""))
    vol_thresh = _safe_float(defaults.get(CONF_ILLUMINANCE_THRESHOLD), DEFAULT_ILLUMINANCE_THRESHOLD)

    schema_dict: dict[Any, Any] = {
        vol.Required(
            CONF_AC_MAX_COOLING,
            default=_safe_float(defaults.get(CONF_AC_MAX_COOLING), DEFAULT_AC_MAX_COOLING),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=100.0, max=20000.0, step=50.0, unit_of_measurement="W", mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Required(
            CONF_AC_AIRFLOW,
            default=_safe_float(defaults.get(CONF_AC_AIRFLOW), DEFAULT_AC_AIRFLOW),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=50.0, max=2000.0, step=10.0, unit_of_measurement="m³/h", mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Optional(CONF_HVAC_MODE, default=hvac_mode_val): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(value=HVAC_MODE_COOLING, label="Cooling (Summer / Cooling)"),
                    selector.SelectOptionDict(value=HVAC_MODE_HEATING, label="Heating (Winter / Heat Pump)"),
                    selector.SelectOptionDict(value=HVAC_MODE_AUTO, label="Auto (Thermostat / Temperature delta)"),
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_CURTAIN_TYPE, default=curtain_type_val): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    selector.SelectOptionDict(value="roller_gaps", label="Indoor Roller Blinds with gaps (blocks 74% heat / 52% total solar)"),
                    selector.SelectOptionDict(value="blackout", label="Sealed Blackout Curtains (blocks 93% heat / 65% total solar)"),
                    selector.SelectOptionDict(value="standard", label="Standard Curtains (blocks 71% heat / 50% total solar)"),
                    selector.SelectOptionDict(value="blinds", label="Light Blinds / Sheers (blocks 50% heat / 35% total solar)"),
                    selector.SelectOptionDict(value="external", label="External Roller Shutters (blocks 100% heat / 70% total solar)"),
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(CONF_ELECTRICITY_RATE, default=vol_rate): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.0, max=100.0, step=0.01, mode=selector.NumberSelectorMode.BOX
            )
        ),
        vol.Optional(CONF_CURRENCY_SYMBOL, default=curr_sym): selector.TextSelector(),
        vol.Optional(CONF_ILLUMINANCE_THRESHOLD, default=vol_thresh): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1.0, max=5000.0, step=5.0, unit_of_measurement="lx", mode=selector.NumberSelectorMode.BOX
            )
        ),
    }
    return vol.Schema(schema_dict)


def get_sensors_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Return Step 3: Sensors & Meteorological inputs schema."""
    schema_dict: dict[Any, Any] = {}

    # Required Sensors
    for conf_key in (CONF_SENSOR_T_IN, CONF_SENSOR_T_OUT, CONF_SENSOR_AC_POWER):
        val = defaults.get(conf_key)
        if val and isinstance(val, str) and val.strip():
            schema_dict[vol.Required(conf_key, default=val)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "input_number", "number"])
            )
        else:
            schema_dict[vol.Required(conf_key)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "input_number", "number"])
            )

    # Optional Climate Thermostat
    clim_val = defaults.get(CONF_SENSOR_CLIMATE)
    if clim_val and isinstance(clim_val, str) and clim_val.strip():
        schema_dict[vol.Optional(CONF_SENSOR_CLIMATE, default=clim_val)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="climate")
        )
    else:
        schema_dict[vol.Optional(CONF_SENSOR_CLIMATE)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="climate")
        )

    # Optional Solar Radiation (fallback to clear-sky if omitted)
    solar_val = defaults.get(CONF_SENSOR_SOLAR)
    if solar_val and isinstance(solar_val, str) and solar_val.strip():
        schema_dict[vol.Optional(CONF_SENSOR_SOLAR, default=solar_val)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["sensor", "input_number", "number"])
        )
    else:
        schema_dict[vol.Optional(CONF_SENSOR_SOLAR)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["sensor", "input_number", "number"])
        )

    # Optional Weather Entity (for cloud coverage)
    weather_val = defaults.get(CONF_SENSOR_WEATHER)
    if weather_val and isinstance(weather_val, str) and weather_val.strip():
        schema_dict[vol.Optional(CONF_SENSOR_WEATHER, default=weather_val)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="weather")
        )
    else:
        schema_dict[vol.Optional(CONF_SENSOR_WEATHER)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="weather")
        )

    # Optional Window Binary Sensor
    win_val = defaults.get(CONF_SENSOR_WINDOW)
    if win_val and isinstance(win_val, str) and win_val.strip():
        schema_dict[vol.Optional(CONF_SENSOR_WINDOW, default=win_val)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="binary_sensor")
        )
    else:
        schema_dict[vol.Optional(CONF_SENSOR_WINDOW)] = selector.EntitySelector(
            selector.EntitySelectorConfig(domain="binary_sensor")
        )

    # Other Optional Sensors
    for conf_key in (
        CONF_SENSOR_ILLUMINANCE,
        CONF_SENSOR_T_AC_EXIT,
        CONF_SENSOR_RH_IN,
        CONF_SENSOR_RH_OUT,
        CONF_SENSOR_WIND_SPEED,
        CONF_SENSOR_WIND_DIRECTION,
    ):
        val = defaults.get(conf_key)
        if val and isinstance(val, str) and val.strip():
            schema_dict[vol.Optional(conf_key, default=val)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "input_number", "number"])
            )
        else:
            schema_dict[vol.Optional(conf_key)] = selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "input_number", "number"])
            )

    return vol.Schema(schema_dict)


class ThermalBalanceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a multi-step config flow wizard for Thermal Balance."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow state."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 1: Room Geometry & Architecture."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_equipment()

        return self.async_show_form(
            step_id="user",
            data_schema=get_geometry_schema(self._data),
            errors=errors,
        )

    async def async_step_equipment(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2: AC Performance, Shading & Financial Settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_sensors()

        return self.async_show_form(
            step_id="equipment",
            data_schema=get_equipment_schema(self._data),
            errors=errors,
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 3: Required and Optional Sensors."""
        errors: dict[str, str] = {}
        hass = getattr(self, "hass", None)

        if user_input is not None:
            if hass and hasattr(hass, "states"):
                for req_key in (CONF_SENSOR_T_IN, CONF_SENSOR_T_OUT, CONF_SENSOR_AC_POWER):
                    eid = user_input.get(req_key)
                    if not eid or hass.states.get(eid) is None:
                        errors[req_key] = "invalid_sensor"

                for opt_key in (
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
                ):
                    eid = user_input.get(opt_key)
                    if eid and hass.states.get(eid) is None:
                        errors[opt_key] = "invalid_sensor"

            if not errors:
                self._data.update(user_input)
                unique_id = f"thermal_balance_{self._data[CONF_SENSOR_T_IN]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                title = f"Thermal Balance ({self._data.get(CONF_ROOM_AREA, 20)} m²)"
                return self.async_create_entry(title=title, data=self._data)

        return self.async_show_form(
            step_id="sensors",
            data_schema=get_sensors_schema(self._data),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 1 of reconfiguration: Room Geometry & Architecture."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if not self._data:
            self._data = {**entry.data, **entry.options}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_reconfigure_equipment()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_geometry_schema(self._data),
            errors=errors,
        )

    async def async_step_reconfigure_equipment(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2 of reconfiguration: AC Performance & Shading."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_reconfigure_sensors()

        return self.async_show_form(
            step_id="reconfigure_equipment",
            data_schema=get_equipment_schema(self._data),
            errors=errors,
        )

    async def async_step_reconfigure_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 3 of reconfiguration: Sensors & Weather."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        hass = getattr(self, "hass", None)

        if user_input is not None:
            if hass and hasattr(hass, "states"):
                for req_key in (CONF_SENSOR_T_IN, CONF_SENSOR_T_OUT, CONF_SENSOR_AC_POWER):
                    eid = user_input.get(req_key)
                    if not eid or hass.states.get(eid) is None:
                        errors[req_key] = "invalid_sensor"

                for opt_key in (
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
                ):
                    eid = user_input.get(opt_key)
                    if eid and hass.states.get(eid) is None:
                        errors[opt_key] = "invalid_sensor"

            if not errors:
                self._data.update(user_input)
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **self._data},
                    reason="reconfigure_successful",
                )

        return self.async_show_form(
            step_id="reconfigure_sensors",
            data_schema=get_sensors_schema(self._data),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get options flow for this handler."""
        return ThermalBalanceOptionsFlow()


class ThermalBalanceOptionsFlow(config_entries.OptionsFlow):
    """Handle 3-step options flow wizard for Thermal Balance."""

    def __init__(self, config_entry: config_entries.ConfigEntry | None = None) -> None:
        """Initialize options flow."""
        if config_entry is not None:
            self.config_entry = config_entry
        self._data: dict[str, Any] = {}

    @property
    def current_config_entry(self) -> config_entries.ConfigEntry:
        """Return active config entry."""
        return getattr(self, "config_entry", None)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 1 of Options Wizard: Room Geometry & Architecture."""
        entry = self.current_config_entry
        errors: dict[str, str] = {}

        if not self._data and entry is not None:
            self._data = {**entry.data, **entry.options}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_equipment()

        return self.async_show_form(
            step_id="init",
            data_schema=get_geometry_schema(self._data),
            errors=errors,
        )

    async def async_step_equipment(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2 of Options Wizard: AC Performance, Shading & Financial Settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_sensors()

        return self.async_show_form(
            step_id="equipment",
            data_schema=get_equipment_schema(self._data),
            errors=errors,
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 3 of Options Wizard: Sensors & Meteorological Inputs."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)

        return self.async_show_form(
            step_id="sensors",
            data_schema=get_sensors_schema(self._data),
            errors=errors,
        )
