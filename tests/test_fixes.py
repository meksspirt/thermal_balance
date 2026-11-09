"""Unit tests for the critical bug fixes in Thermal Balance."""
import asyncio
from datetime import datetime, timezone
import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from mock_ha import MockConfigEntry, MockHomeAssistant, MockState, setup_mock_homeassistant

setup_mock_homeassistant()

from custom_components.thermal_balance import async_setup
from custom_components.thermal_balance.binary_sensor import (
    BINARY_SENSOR_TYPES,
    ThermalBalanceBinarySensor,
)
from custom_components.thermal_balance.const import (
    BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS,
    BINARY_SENSOR_RECOMMEND_OPEN_WINDOW,
    CONF_AC_MAX_COOLING,
    CONF_CURTAIN_TYPE,
    CONF_ELECTRICITY_RATE,
    CONF_HVAC_MODE,
    CONF_ROOM_AREA,
    CONF_SENSOR_AC_POWER,
    CONF_SENSOR_ILLUMINANCE,
    CONF_SENSOR_T_IN,
    CONF_SENSOR_T_OUT,
    CONF_SENSOR_WEATHER,
    DOMAIN,
    HVAC_MODE_COOLING,
    HVAC_MODE_HEATING,
    NUMBER_ELECTRICITY_RATE,
    SELECT_CURTAIN_TYPE,
    SELECT_HVAC_MODE,
    SENSOR_INSTANT_HEAT_GAIN,
    SERVICE_CALCULATE_COOLING_NEEDS,
)
from custom_components.thermal_balance.coordinator import ThermalBalanceCoordinator
from custom_components.thermal_balance.model import CURTAIN_TYPE_FACTORS
from custom_components.thermal_balance.number import ThermalBalanceElectricityRateNumber
from custom_components.thermal_balance.select import (
    ThermalBalanceCurtainTypeSelect,
    ThermalBalanceHVACModeSelect,
)


class TestThermalBalanceBugFixes(unittest.TestCase):
    """Test suite covering the 4 critical bug fixes."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.hass = MockHomeAssistant()
        self.entry_data = {
            CONF_ROOM_AREA: 20.0,
            CONF_AC_MAX_COOLING: 3350.0,
            CONF_ELECTRICITY_RATE: 4.32,
            CONF_SENSOR_T_IN: "sensor.indoor_temp",
            CONF_SENSOR_T_OUT: "sensor.outdoor_temp",
            CONF_SENSOR_AC_POWER: "sensor.ac_power",
            CONF_SENSOR_WEATHER: "weather.forecast",
            CONF_SENSOR_ILLUMINANCE: "sensor.room_lux",
            CONF_HVAC_MODE: HVAC_MODE_COOLING,
            CONF_CURTAIN_TYPE: "roller_gaps",
        }
        self.entry = MockConfigEntry(data=self.entry_data, options={})
        self.coordinator = ThermalBalanceCoordinator(self.hass, self.entry)
        self.entry.runtime_data = self.coordinator
        self.hass.config_entries.add(self.entry)

    def test_window_open_heuristic_without_sensor(self) -> None:
        """Bug 2: Test that window_is_open defaults to False when no window sensor is configured,
        even if AC power is 0W, and recommend_open_window can trigger."""
        self.assertFalse(self.coordinator.has_window_sensor)

        # Set AC off (power = 0 W)
        self.coordinator.ac_power_val = 0.0
        self.coordinator.t_in_val = 26.0
        self.coordinator.t_out_val = 18.0
        self.coordinator.solar_val = 0.0
        self.coordinator.wind_speed_val = 2.0
        self.coordinator.curtains_closed = False

        self.coordinator.recalculate()

        # Window must NOT be assumed open
        self.assertFalse(self.coordinator.window_is_open)
        heat_gain_attrs = self.coordinator.extra_attributes.get(SENSOR_INSTANT_HEAT_GAIN, {})
        self.assertEqual(heat_gain_attrs.get("window_mode"), "no_sensor")

        # Because window is NOT open and outside is cooler (18°C vs 26°C), recommend_open_window MUST be True
        self.assertTrue(self.coordinator.data.get(BINARY_SENSOR_RECOMMEND_OPEN_WINDOW))
        self.assertTrue(heat_gain_attrs.get("recommend_open_window"))

    def test_recommendations_exported_in_heat_gain_attributes(self) -> None:
        """Bug 1: Test that recommend_open_window and recommend_close_curtains are in extra_attributes."""
        # 1. Open window recommendation
        self.coordinator.t_in_val = 26.0
        self.coordinator.t_out_val = 19.0
        self.coordinator.solar_val = 0.0
        self.coordinator.recalculate()

        heat_gain_attrs = self.coordinator.extra_attributes.get(SENSOR_INSTANT_HEAT_GAIN, {})
        self.assertIn("recommend_open_window", heat_gain_attrs)
        self.assertIn("recommend_close_curtains", heat_gain_attrs)
        self.assertTrue(heat_gain_attrs["recommend_open_window"])
        self.assertFalse(heat_gain_attrs["recommend_close_curtains"])

        # 2. Close curtains recommendation (sunny day, curtains open)
        self.hass.states.set("sun.sun", "above_horizon", {"elevation": 60.0, "azimuth": 180.0})
        self.hass.states.set("weather.forecast", "sunny", {"cloud_coverage": 0})
        self.coordinator.t_in_val = 24.0
        self.coordinator.t_out_val = 30.0
        self.coordinator.curtains_closed = False
        self.coordinator.recalculate()

        heat_gain_attrs = self.coordinator.extra_attributes.get(SENSOR_INSTANT_HEAT_GAIN, {})
        self.assertFalse(heat_gain_attrs["recommend_open_window"])
        self.assertTrue(heat_gain_attrs["recommend_close_curtains"])

    def test_select_options_saved_and_restore_entity_not_overwriting(self) -> None:
        """Bug 3: Test that changing select saves to entry.options, and restore state does not overwrite options flow."""
        hvac_select = ThermalBalanceHVACModeSelect(self.coordinator, self.entry)
        hvac_select.hass = self.hass

        # Changing option saves to entry.options
        asyncio.run(hvac_select.async_select_option(HVAC_MODE_HEATING))
        self.assertEqual(self.coordinator.hvac_mode, HVAC_MODE_HEATING)
        self.assertEqual(self.entry.options.get(SELECT_HVAC_MODE), HVAC_MODE_HEATING)

        # Now simulate restart where entry.options has HEATING, but last_state was COOLING
        hvac_select._mock_last_state = MockState(state=HVAC_MODE_COOLING)
        asyncio.run(hvac_select.async_added_to_hass())
        # Coordinator must NOT be reverted to COOLING because options has precedence!
        self.assertEqual(self.coordinator.hvac_mode, HVAC_MODE_HEATING)

        # Curtain type select test
        curtain_select = ThermalBalanceCurtainTypeSelect(self.coordinator, self.entry)
        curtain_select.hass = self.hass

        asyncio.run(curtain_select.async_select_option("blackout"))
        self.assertEqual(self.coordinator.curtain_type, "blackout")
        self.assertEqual(self.entry.options.get(SELECT_CURTAIN_TYPE), "blackout")

        # When options has BLACKOUT, last_state="roller_gaps" must not overwrite it
        curtain_select._mock_last_state = MockState(state="roller_gaps")
        asyncio.run(curtain_select.async_added_to_hass())
        self.assertEqual(self.coordinator.curtain_type, "blackout")

    def test_number_options_saved_and_restore_entity_not_overwriting(self) -> None:
        """Bug 3: Test that changing number saves to entry.options, and restore state does not overwrite options flow."""
        num_entity = ThermalBalanceElectricityRateNumber(self.coordinator, self.entry)
        num_entity.hass = self.hass

        # Setting value persists to entry.options
        asyncio.run(num_entity.async_set_native_value(6.75))
        self.assertEqual(self.coordinator.electricity_rate, 6.75)
        self.assertEqual(self.entry.options.get(NUMBER_ELECTRICITY_RATE), 6.75)

        # On restart/reload, if options has 6.75, last_state=4.32 must not overwrite it
        num_entity._mock_last_state = MockState(state="4.32")
        asyncio.run(num_entity.async_added_to_hass())
        self.assertEqual(self.coordinator.electricity_rate, 6.75)

        # But if entry.options does not have the key, last_state should be restored
        fresh_entry = MockConfigEntry(data={CONF_ROOM_AREA: 20.0}, options={})
        fresh_coord = ThermalBalanceCoordinator(self.hass, fresh_entry)
        fresh_num = ThermalBalanceElectricityRateNumber(fresh_coord, fresh_entry)
        fresh_num.hass = self.hass
        fresh_num._mock_last_state = MockState(state="5.20")
        asyncio.run(fresh_num.async_added_to_hass())
        self.assertEqual(fresh_coord.electricity_rate, 5.20)

    def test_service_calculate_cooling_needs_uses_curtain_type_and_model(self) -> None:
        """Bug 4: Test calculate_cooling_needs uses model.py calculations taking curtain type into account."""
        asyncio.run(async_setup(self.hass, {}))

        # Run service with blackout curtains
        self.coordinator.curtain_type = "blackout"
        resp_blackout = asyncio.run(
            self.hass.services.async_call(
                DOMAIN,
                SERVICE_CALCULATE_COOLING_NEEDS,
                {
                    "entry_id": self.entry.entry_id,
                    "target_temperature": 23.0,
                    "outdoor_temperature": 32.0,
                    "solar_irradiance": 600.0,
                    "curtains_closed": True,
                },
            )
        )

        # Run service with roller gaps curtains
        self.coordinator.curtain_type = "roller_gaps"
        resp_roller = asyncio.run(
            self.hass.services.async_call(
                DOMAIN,
                SERVICE_CALCULATE_COOLING_NEEDS,
                {
                    "entry_id": self.entry.entry_id,
                    "target_temperature": 23.0,
                    "outdoor_temperature": 32.0,
                    "solar_irradiance": 600.0,
                    "curtains_closed": True,
                },
            )
        )

        # Blackout curtains block more solar radiation (g=0.15) than roller_gaps (g=0.35),
        # so blackout must require LESS cooling power than roller_gaps.
        self.assertLess(resp_blackout["required_power_w"], resp_roller["required_power_w"])
        self.assertLess(resp_blackout["equilibrium_temperature_c"], resp_roller["equilibrium_temperature_c"])
        self.assertGreater(resp_blackout["estimated_cop"], 1.5)

    def test_binary_sensor_close_curtains_savings_attributes(self) -> None:
        """Bug 4: Test that binary_sensor recommend_close_curtains attributes compute savings accurately."""
        curtain_bin_desc = next(
            d for d in BINARY_SENSOR_TYPES if d.key == BINARY_SENSOR_RECOMMEND_CLOSE_CURTAINS
        )
        sensor = ThermalBalanceBinarySensor(self.coordinator, curtain_bin_desc, self.entry)

        self.hass.states.set("sun.sun", "above_horizon", {"elevation": 60.0, "azimuth": 180.0})
        self.hass.states.set("weather.forecast", "sunny", {"cloud_coverage": 0})
        self.coordinator.curtain_type = "blackout"
        self.coordinator.curtains_closed = False
        self.coordinator.recalculate()

        attrs = sensor.extra_state_attributes
        self.assertIn("potential_heat_reduction_w", attrs)
        self.assertIn("potential_daily_savings", attrs)

        # For blackout, saved_fraction is 0.65 (vs roller_gaps 0.52)
        saved_fraction = CURTAIN_TYPE_FACTORS["blackout"][1]
        self.assertEqual(saved_fraction, 0.65)

        # With solar radiation entering, reduction must be positive
        self.assertGreater(attrs["potential_heat_reduction_w"], 0.0)

    def test_quality_scale_entity_translations_and_no_attr_name(self) -> None:
        """Quality Scale: Test that entities do not hardcode names and define translation_keys."""
        from custom_components.thermal_balance.button import (
            ThermalBalanceResetDailyButton,
            ThermalBalanceResetKFactorButton,
        )
        from custom_components.thermal_balance.sensor import SENSOR_TYPES

        # Sensor descriptions must not have name and must have translation_key
        for desc in SENSOR_TYPES:
            self.assertIsNone(desc.name)
            self.assertEqual(desc.translation_key, desc.key)

        # Binary sensors must not have name and must have translation_key
        for bin_desc in BINARY_SENSOR_TYPES:
            self.assertIsNone(bin_desc.name)
            self.assertEqual(bin_desc.translation_key, bin_desc.key)

        # Buttons must not hardcode _attr_name
        b1 = ThermalBalanceResetDailyButton(self.coordinator, self.entry)
        b2 = ThermalBalanceResetKFactorButton(self.coordinator, self.entry)
        self.assertIsNone(getattr(b1, "_attr_name", None))
        self.assertIsNone(getattr(b2, "_attr_name", None))
        self.assertEqual(b1._attr_translation_key, "reset_daily")
        self.assertEqual(b2._attr_translation_key, "reset_k_factor")

        # Number must not hardcode _attr_name
        num = ThermalBalanceElectricityRateNumber(self.coordinator, self.entry)
        self.assertIsNone(getattr(num, "_attr_name", None))
        self.assertEqual(num._attr_translation_key, "electricity_rate")

        # Selects must not hardcode _attr_name
        sel_hvac = ThermalBalanceHVACModeSelect(self.coordinator, self.entry)
        sel_curt = ThermalBalanceCurtainTypeSelect(self.coordinator, self.entry)
        self.assertIsNone(getattr(sel_hvac, "_attr_name", None))
        self.assertIsNone(getattr(sel_curt, "_attr_name", None))
        self.assertEqual(sel_hvac._attr_translation_key, "hvac_mode")
        self.assertEqual(sel_curt._attr_translation_key, "curtain_type")

    def test_quality_scale_entity_categories(self) -> None:
        """Quality Scale: Test entity_category assignments for config and diagnostic entities."""
        from homeassistant.const import EntityCategory
        from custom_components.thermal_balance.button import (
            ThermalBalanceResetDailyButton,
            ThermalBalanceResetKFactorButton,
        )
        from custom_components.thermal_balance.const import SENSOR_EMPIRICAL_K_FACTOR
        from custom_components.thermal_balance.sensor import SENSOR_TYPES

        # Config categories
        b1 = ThermalBalanceResetDailyButton(self.coordinator, self.entry)
        b2 = ThermalBalanceResetKFactorButton(self.coordinator, self.entry)
        num = ThermalBalanceElectricityRateNumber(self.coordinator, self.entry)
        sel_hvac = ThermalBalanceHVACModeSelect(self.coordinator, self.entry)
        sel_curt = ThermalBalanceCurtainTypeSelect(self.coordinator, self.entry)

        self.assertEqual(b1.entity_category, EntityCategory.CONFIG)
        self.assertEqual(b2.entity_category, EntityCategory.CONFIG)
        self.assertEqual(num.entity_category, EntityCategory.CONFIG)
        self.assertEqual(sel_hvac.entity_category, EntityCategory.CONFIG)
        self.assertEqual(sel_curt.entity_category, EntityCategory.CONFIG)

        # Diagnostic category for empirical K-factor
        k_desc = next(d for d in SENSOR_TYPES if d.key == SENSOR_EMPIRICAL_K_FACTOR)
        self.assertEqual(k_desc.entity_category, EntityCategory.DIAGNOSTIC)

    def test_quality_scale_config_flow_unique_id_and_validation(self) -> None:
        """Quality Scale: Test unique ID protection, duplicate abort, and sensor validation."""
        from homeassistant.data_entry_flow import AbortFlow
        from custom_components.thermal_balance.config_flow import (
            ThermalBalanceConfigFlow,
            ThermalBalanceOptionsFlow,
        )

        flow = ThermalBalanceConfigFlow()
        flow.hass = self.hass

        # Set indoor temp sensor state in hass
        self.hass.states.set("sensor.indoor_temp", "22.5")
        self.hass.states.set("sensor.outdoor_temp", "15.0")
        # Do NOT set sensor.ac_power

        step3_data = {
            CONF_SENSOR_T_IN: "sensor.indoor_temp",
            CONF_SENSOR_T_OUT: "sensor.outdoor_temp",
            CONF_SENSOR_AC_POWER: "sensor.non_existent_power",
        }
        res = asyncio.run(flow.async_step_sensors(step3_data))
        self.assertEqual(res["type"], "form")
        self.assertEqual(res["errors"].get(CONF_SENSOR_AC_POWER), "invalid_sensor")

        # Now set the power sensor so validation passes
        self.hass.states.set("sensor.ac_power", "850.0")
        step3_valid = {
            CONF_SENSOR_T_IN: "sensor.indoor_temp",
            CONF_SENSOR_T_OUT: "sensor.outdoor_temp",
            CONF_SENSOR_AC_POWER: "sensor.ac_power",
        }
        res_valid = asyncio.run(flow.async_step_sensors(step3_valid))
        self.assertEqual(res_valid["type"], "create_entry")
        self.assertEqual(flow.unique_id, "thermal_balance_sensor.indoor_temp")

        # Test duplicate entry abort
        flow2 = ThermalBalanceConfigFlow()
        flow2.hass = self.hass
        duplicate_entry = MockConfigEntry(
            entry_id="dup_1",
            unique_id="thermal_balance_sensor.indoor_temp",
        )
        self.hass.config_entries.add(duplicate_entry)

        with self.assertRaises(AbortFlow) as ctx:
            asyncio.run(flow2.async_step_sensors(step3_valid))
        self.assertEqual(ctx.exception.reason, "already_configured")

        # Test modern OptionsFlow
        opt_flow = ThermalBalanceConfigFlow.async_get_options_flow(self.entry)
        self.assertIsInstance(opt_flow, ThermalBalanceOptionsFlow)

    def test_quality_scale_availability_and_logging(self) -> None:
        """Quality Scale: Test coordinator availability tracking and logging on mandatory sensor state change."""
        from unittest.mock import MagicMock
        from custom_components.thermal_balance.sensor import (
            SENSOR_TYPES,
            ThermalBalanceSensor,
        )

        sensor_desc = next(d for d in SENSOR_TYPES if d.key == SENSOR_INSTANT_HEAT_GAIN)
        sensor_entity = ThermalBalanceSensor(self.coordinator, self.entry, sensor_desc)

        # Initially, all mandatory sensors exist in coordinator
        self.assertTrue(self.coordinator.last_update_success)
        self.assertTrue(sensor_entity.available)

        # Indoor temp becomes unavailable
        event_unavail = MagicMock()
        event_unavail.data = {
            "entity_id": self.coordinator.sensor_t_in,
            "new_state": MockState("unavailable"),
        }
        self.coordinator._async_handle_state_change(event_unavail)

        self.assertFalse(self.coordinator.last_update_success)
        self.assertFalse(sensor_entity.available)

        # Indoor temp recovers
        event_avail = MagicMock()
        event_avail.data = {
            "entity_id": self.coordinator.sensor_t_in,
            "new_state": MockState("23.5"),
        }
        self.coordinator._async_handle_state_change(event_avail)

        self.assertTrue(self.coordinator.last_update_success)
        self.assertTrue(sensor_entity.available)

    def test_quality_scale_parallel_updates(self) -> None:
        """Quality Scale: Test PARALLEL_UPDATES = 0 across all platform modules."""
        import custom_components.thermal_balance.binary_sensor as bs
        import custom_components.thermal_balance.button as bt
        import custom_components.thermal_balance.number as nb
        import custom_components.thermal_balance.select as sl
        import custom_components.thermal_balance.sensor as sn

        self.assertEqual(bs.PARALLEL_UPDATES, 0)
        self.assertEqual(bt.PARALLEL_UPDATES, 0)
        self.assertEqual(nb.PARALLEL_UPDATES, 0)
        self.assertEqual(sl.PARALLEL_UPDATES, 0)
        self.assertEqual(sn.PARALLEL_UPDATES, 0)

    def test_quality_scale_non_blocking_frontend_registration(self) -> None:
        """Quality Scale: Test non-blocking frontend registration via async_add_executor_job."""
        from custom_components.thermal_balance import _async_register_frontend
        import custom_components.thermal_balance as tb_mod

        # Reset flag to test registration
        tb_mod._FRONTEND_REGISTERED = False
        asyncio.run(_async_register_frontend(self.hass))
        self.assertTrue(tb_mod._FRONTEND_REGISTERED)


if __name__ == "__main__":
    unittest.main()
