# 🚀 Thermal Balance v2.2.0 — Quality Scale, Multi-Room Card, Focus Stability & Thermodynamic Bugfixes

A major feature, stability, and Quality Scale release resolving critical thermodynamic and state restoration bugs, bringing multi-instance room support to the Lovelace card, fixing editor focus loss, supporting Lovelace Sections Grid, full bilingual entity and card translations, and 100% test coverage!

---

## 🌟 What's New in v2.2.0

### 🐛 1. Critical Thermodynamic & State Fixes
* **Lovelace Recommendation Banners Fixed**:
  * Extended `autoDiscoverEntities` to discover both `sensor.` and `binary_sensor.` entities.
  * Added `_getBoolState` in card to correctly interpret `'on'`, `'off'`, `'true'`, `'1'` states instead of returning `NaN` from `parseFloat`.
  * Exposed `recommend_open_window` and `recommend_close_curtains` directly in `extra_attributes` of `sensor.*_instant_heat_gain`.
* **Default Window State Heuristic**:
  * When no window contact sensor (`CONF_SENSOR_WINDOW`) is configured, `window_is_open` now defaults to `False` (closed).
  * Eliminated incorrect heuristic that assumed windows were open whenever AC power fell below 20W, which previously inflated room infiltration/HLC by 1.5–2× and permanently blocked free cooling recommendations.
* **Options Flow & RestoreEntity Conflict Resolved**:
  * Fixed bug where changing HVAC mode, curtain type, or electricity tariff in Options Flow would be overwritten on reload by `RestoreEntity.async_added_to_hass` restoring stale entity states.
  * Interactive UI controls now persist their state updates to `config_entry.options` via `hass.config_entries.async_update_entry`.
* **Physics Formulas Synchronization**:
  * Synchronized solar gains and wind-driven infiltration calculations between `calculate_cooling_needs` service, `insufficient_cooling_capacity` binary sensor, and the core thermodynamic model.

### 🏛️ 2. Home Assistant Quality Scale Compliance
* **Entity & Icon Translations (`has-entity-name`, `entity-translations`)**:
  * Removed hardcoded English `_attr_name` across `sensor.py`, `binary_sensor.py`, `button.py`, `number.py`, and `select.py`.
  * Assigned `translation_key` to all 15 sensors and 3 binary sensors.
  * Fully populated `strings.json`, `translations/en.json`, `translations/ru.json`, and `icons.json`.
* **Entity Categories (`entity-category`)**:
  * Assigned `EntityCategory.CONFIG` to `select.hvac_mode`, `select.curtain_type`, `number.electricity_rate`, `button.reset_daily`, `button.reset_k_factor`.
  * Assigned `EntityCategory.DIAGNOSTIC` to `sensor.empirical_k_factor`.
* **Config Flow Protection & Modernization**:
  * Added `async_set_unique_id` (`thermal_balance_{CONF_SENSOR_T_IN}`) with duplicate entry abortion (`_abort_if_unique_id_configured`).
  * Added sensor validation handling with `invalid_sensor` error feedback.
  * Modernized `ThermalBalanceOptionsFlow` initialization for Home Assistant 2024.11+.
* **Availability Monitoring (`entity-unavailable`, `log-when-unavailable`)**:
  * Coordinator monitors required sensors (`sensor_t_in`, `sensor_t_out`, `sensor_ac_power`) and sets `last_update_success = False` with warning logs on loss and info logs on recovery.
* **Concurrency (`parallel-updates`)**:
  * Declared `PARALLEL_UPDATES: Final = 0` across all platform modules.
* **Non-blocking Card Registration**:
  * Registered static card resources asynchronously via `hass.async_add_executor_job` in `async_setup`.

### 🎴 3. Lovelace Card Modernization (`thermal-balance-card.js`)
* **Visual Editor Focus Stability**:
  * `ThermalBalanceCardEditor.set hass(hass)` now only re-renders on initial mount or when the set of entity IDs actually changes, eliminating focus loss while typing custom titles or picking entities.
  * Added input cursor and selection restoration (`selectionStart`/`selectionEnd`) across edits.
* **Multi-Instance / Multi-Room Support**:
  * Added `autoDiscoverInstances(hass)` to detect multiple rooms/instances and extract their prefixes and friendly names.
  * Added a dedicated **Room / Instance (Auto-detect)** dropdown to the visual editor.
  * All 15 sensors can now be configured individually or auto-discovered per room prefix.
  * Binary sensors (`binary_sensor.`) are now included in the entity picker.
* **Lovelace Sections Grid Support**:
  * Added `static getGridOptions(hass, config)` and `getGridOptions()` returning `{ columns: 12, rows: 6, min_columns: 6, min_rows: 4 }` (and `{ rows: 4, min_rows: 3 }` in compact mode).
* **Card Picker Live Preview**:
  * Enabled `preview: true` and specified `documentationURL` in `window.customCards`.
  * Fallback preview renders mock thermodynamic gauges and metrics cleanly before sensors are bound.
* **Full Russian UI Localization**:
  * Translated all AC Performance table rows (*Exit Temp*, *Sensible*, *Latent*, *SHR*, *Enthalpy*, *Airflow*, *Dew Pt*).
  * Added translation mapping for dynamic insulation grades (*Excellent*, *Good*, *Average*, *Poor*) and curtain detection notes.
  * Localized units (*ч*, *мин*, *м/с*, */ ч*, */день*).

---

## 🧪 Testing & Verification
* Full test suite with **77 unit tests** passing in `tests/`.
* JavaScript syntax verified with Node.js (`node -c`).
* Clean JSON schemas in `translations/`, `strings.json`, and `icons.json`.
