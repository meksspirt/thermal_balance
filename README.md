# 🌡️ Thermal Balance — Home Assistant Custom Component & Premium Card

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)
[![version](https://img.shields.io/badge/version-v2.2.0-blue.svg)](https://github.com/meksspirt/thermal_balance/releases/latest)
[![Tests](https://github.com/meksspirt/thermal_balance/actions/workflows/test.yml/badge.svg)](https://github.com/meksspirt/thermal_balance/actions)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=https%3A%2F%2Fgithub.com%2Fmeksspirt%2Fthermal_balance&category=Integration)

**Thermal Balance** is a physics-based custom integration and Lovelace dashboard card for Home Assistant. It models room thermodynamics as an open system in both **cooling** (summer AC) and **heating** (winter heat pump) modes. It calculates real-time heat flux, clear-sky solar irradiance, Angle of Incidence (AOI) solar geometry, sensible/latent AC heat output, natural ventilation infiltration, smart curtain shading, dynamic $dT/dt$ $K$-factor auto-calibration, temperature shift forecasts, electricity cost tracking, and smart advice alerts.

---

## 🌟 Key Features

* **❄️🔥 Year-Round HVAC Mode Support (Cooling & Heating / Heat Pump)**:
  * Full thermodynamic support for **Cooling** ($P_{\text{net}} = P_{\text{gain}} - P_{\text{cooling}}$) and **Heating** ($P_{\text{net}} = P_{\text{gain}} + P_{\text{heating}}$).
  * Selectable operation mode: `Cooling`, `Heating`, or `Auto` (automatically follows thermostat `climate.*` entity state or outdoor temperature delta).
* **☀️ Astronomical Clear-Sky Solar Estimation & AOI Geometry**:
  * **Physical solar sensor NOT required!** Built-in **Haurwitz Clear-Sky Model** and **Kasten-Czeplak Cloud Cover Attenuation** automatically compute solar radiation ($W/m^2$) based on sun elevation (`sun.sun`) and optional weather cloud coverage (`weather.*`).
  * **Angle of Incidence (AOI)** geometry accurately calculates direct solar heat entry vs diffuse light based on window azimuth ($0^\circ \dots 360^\circ$).
* **🧱 Dynamic $dT/dt$ Thermal Mass $K$-Factor Calibration**:
  * Dynamic heat mass compensation ($P_{\text{steady}} = P_{\text{cooling}} - P_{\text{solar}} - C_{\text{total}} \cdot \frac{dT}{dt}$) filters out transient room cooldown/warmup slopes, preventing false building insulation degradation spikes.
* **🎛️ Interactive Controls & Entities**:
  * `select.thermal_balance_hvac_mode`: Switch between Cooling, Heating, and Auto.
  * `select.thermal_balance_curtain_type`: Change window shading type on the fly (`roller_gaps`, `blackout`, `standard`, `blinds`, `external`).
  * `button.thermal_balance_reset_daily`: Instant reset of daily kWh and cost counters.
  * `button.thermal_balance_reset_k_factor`: Reset learned building insulation samples.
  * `number.thermal_balance_electricity_rate`: Live electricity tariff adjustment (supports multi-tariff automations).
* **💡 Smart Advice & Analytical Sensors**:
  * `sensor.thermal_balance_equilibrium_temperature`: Passive room temperature without HVAC.
  * `sensor.thermal_balance_required_ac_power`: Required HVAC thermal power to hold target 23°C.
  * `binary_sensor.thermal_balance_recommend_open_window`: Triggers when outdoor air is cooler than room air, suggesting natural free cooling.
  * `binary_sensor.thermal_balance_recommend_close_curtains`: Recommends shading during high solar exposure.
  * `binary_sensor.thermal_balance_insufficient_cooling_capacity`: Alerts when thermal gain exceeds HVAC capacity.
* **⚡ Official Home Assistant Actions (Services)**:
  * `thermal_balance.reset_accumulators`: Immediately zero all accumulators.
  * `thermal_balance.recalibrate_k_factor`: Clear calibration history.
  * `thermal_balance.calculate_cooling_needs`: On-demand thermal analysis returning `ServiceResponse`.
* **🧙‍♂️ 3-Step Wizard Config Flow & Gold Quality Reconfiguration**:
  * Clean 3-step setup: **Step 1:** Room Geometry $\rightarrow$ **Step 2:** Equipment & Shading $\rightarrow$ **Step 3:** Sensors.
  * Full **Home Assistant Gold Quality Scale `async_step_reconfigure`** support.
* **📱 Premium Lovelace Dashboard Card (`custom:thermal-balance-card`)**:
  * **🌐 Full i18n**: Automatic RU/EN language detection via `hass.locale.language`.
  * **📱 Compact Mobile Mode (`compact: true`)**: Streamlined single-column layout for smartphones.
  * **❄️🔥 Seasonal Theme Adaptation**: Cool cyan neon in cooling mode vs warm amber glow in heating mode.
  * Interactive 24h ECharts trend graph and real-time SVG analog gauges.

---

## 📖 Complete Documentation & Guide

For detailed physics equations, configuration walkthrough, full entity tables, card styling, and FAQ, read our [📖 GUIDE.md Documentation](GUIDE.md).

---

## 📁 Repository Structure

```
custom_components/thermal_balance/
├── __init__.py                # Integration setup, services & Lovelace resource registration
├── config_flow.py             # 3-step Wizard Config, Options & Reconfigure Flow
├── const.py                   # Constants, default coefficients & entity IDs
├── coordinator.py             # Thin Home Assistant event glue coordinator
├── engine.py                  # Pure domain calculations, calibrator & advisors
├── model.py                   # Pure thermodynamic & solar physics engine
├── sensor.py                  # Analytical sensors & accumulators
├── binary_sensor.py           # Smart recommendation & capacity binary sensors
├── button.py                  # Daily accumulator & K-factor reset buttons
├── number.py                  # Dynamic electricity tariff entity
├── select.py                  # HVAC mode & curtain type select entities
├── diagnostics.py             # Home Assistant Diagnostics dump support
├── quality_scale.yaml         # Home Assistant Quality Scale compliance rules
├── services.yaml              # Official Home Assistant action descriptions
├── icons.json                 # Quality scale MDI icon localization
├── thermal-balance-card.js    # Premium Lovelace card (i18n, compact view, themes)
├── echarts.min.js             # Built-in ECharts graphing engine
├── manifest.json              # Integration manifest
├── hacs.json                  # HACS repository configuration
├── strings.json               # Localized UI schema strings
└── translations/
    ├── en.json                # English UI translations
    └── ru.json                # Russian UI translations
.github/workflows/
└── test.yml                   # CI/CD automated test & HACS validation suite
tests/
├── mock_ha.py                 # Standalone Home Assistant test harness
├── test_model.py              # Physics & clear-sky thermodynamic unit tests
├── test_engine.py             # Pure domain engine, tracker, calibrator tests
├── test_coordinator.py        # Coordinator, sunrise/sunset & action tests
├── test_config_flow.py        # 3-step Config/Options/Reconfigure flow tests
├── test_diagnostics.py        # Diagnostic dump tests
└── test_services.py           # Services & ServiceValidationError tests
```

---

## 🚀 Installation

### Option 1: HACS (Recommended)

1. Open **HACS** $\rightarrow$ **Integrations** $\rightarrow$ **3 dots (top right)** $\rightarrow$ **Custom Repositories**.
2. Add Repository URL: `https://github.com/meksspirt/thermal_balance`
3. Category: **Integration**.
4. Click **Install**.
5. Restart Home Assistant.

### Option 2: Manual Installation

1. Copy the `custom_components/thermal_balance` directory into your Home Assistant `<config>/custom_components/` folder.
2. Restart Home Assistant.

---

## ⚙️ Setup & Configuration

1. In Home Assistant, navigate to **Settings** $\rightarrow$ **Devices & Services** $\rightarrow$ **Add Integration**.
2. Search for **Thermal Balance**.
3. Follow the 3-step setup wizard:
   * **Step 1: Room Geometry & Architecture** (Floor area $m^2$, ceiling height $m$, glazing area $m^2$, wall & window $U$-values).
   * **Step 2: Equipment & Shading** (Rated AC power $W$, airflow volume $m^3/h$, curtain type, electricity tariff).
   * **Step 3: Sensors & Meteorological Inputs** (Required: Indoor Temp, Outdoor Temp, AC Power. Optional: Weather, Climate, Window contact, Lux sensor, Humidity).
4. Click **Submit**.

---

## 🎨 Lovelace Dashboard Card

Add the custom card to your dashboard:

```yaml
type: custom:thermal-balance-card
compact: true               # Set true for mobile dashboards
title: "Bedroom Climate"    # Optional custom title
```

---

## 📄 License

MIT License © [meksspirt](https://github.com/meksspirt)
