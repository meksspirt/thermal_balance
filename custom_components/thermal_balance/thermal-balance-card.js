/**
 * Thermal Balance Card — Premium Home Assistant Lovelace Card
 * Pure vanilla JS Custom Element with Visual UI Editor & Auto-Discovery
 *
 * Registered as: custom:thermal-balance-card
 * Editor registered as: thermal-balance-card-editor
 */

const TRANSLATIONS = {
  en: {
    title: 'Thermal Balance',
    editor_title: 'Thermal Balance Configuration',
    instance_selector: 'Room / Instance (Auto-detect)',
    compact_view: 'Compact Mode (Mobile)',
    card_title_label: 'Custom Card Title (Optional)',
    heat_gain_sensor: 'Heat Gain Sensor',
    ac_cooling_sensor: 'AC Cooling / Heating Sensor',
    net_balance_sensor: 'Net Balance Sensor',
    ac_cop_sensor: 'AC COP Sensor',
    time_to_1c_sensor: 'Time to 1°C Sensor',
    daily_balance_sensor: 'Daily Balance Sensor',
    total_balance_sensor: 'Total Balance Sensor',
    heat_absorbed_sensor: 'Heat Absorbed Sensor',
    ac_energy_sensor: 'AC Thermal Energy Sensor',
    condensation_rate_sensor: 'Condensation Rate Sensor',
    empirical_k_factor_sensor: 'Empirical K-Factor Sensor',
    ac_cost_sensor: 'AC Energy Cost Sensor',
    daily_savings_sensor: 'Daily Shading Savings Sensor',
    rec_open_window_sensor: 'Open Window Recommendation Sensor',
    rec_close_curtains_sensor: 'Close Curtains Recommendation Sensor',
    heat_mode: 'Heat Mode',
    cool_mode: 'Cool Mode',
    stable: 'Stable',
    heat_gain: 'Heat Gain',
    heat_loss: 'Heat Loss',
    ac_cooling: 'AC Cooling',
    ac_heating: 'AC Heating',
    net_balance: 'Net Balance',
    ventilation: 'Ventilation',
    to_1c: 'To 1°C',
    condensation: 'Condensation',
    vent_heat_exchange: 'Ventilation & Heat Exchange',
    window: 'Window',
    window_open: 'Open',
    window_closed: 'Closed',
    wind: 'Wind',
    air_change: 'Air Change (ACH)',
    curtains: 'Curtains',
    curtains_closed: 'Closed',
    curtains_open: 'Open',
    curtains_note_no_sensor: 'Illuminance sensor not configured',
    curtains_note_night: 'Night: auto curtain detection disabled (lux threshold not applied)',
    solar: 'Solar',
    walls: 'Walls',
    k_factor_actual: 'K-Factor (Actual)',
    insulation: 'Insulation',
    estimated: 'Estimated',
    grade_excellent: 'Excellent (passport)',
    grade_good: 'Good (moderate)',
    grade_average: 'Average (thermal bridges)',
    grade_poor: 'Poor (drafts)',
    window_open_k_note: 'Window is open — K-factor is unreliable',
    ac_cooling_perf: 'AC Cooling Performance',
    heating_perf: 'Heating Performance (Heat Pump)',
    ac_dt: 'ΔT AC',
    exit_temp_meas: 'Exit Temp (Meas)',
    exit_temp: 'Exit Temp',
    exit_temp_calc: 'Exit Temp (Calc)',
    sensible_heat: 'Sensible',
    sensible_heat_heating: 'Sensible Heat',
    latent_heat: 'Latent',
    shr: 'SHR',
    enthalpy: 'Enthalpy',
    airflow: 'Airflow',
    dew_point_in: 'Dew Pt In',
    dew_point_out: 'Dew Pt Out',
    trend_24h: '24h Thermal Trend',
    heat: 'Heat',
    cooling: 'Cooling',
    heating: 'Heating',
    net: 'Net',
    energy_cost_intel: 'Energy & Cost Intelligence',
    daily_balance: 'Daily Balance',
    total_balance: 'Total Balance',
    heat_absorbed: 'Heat Absorbed',
    ac_energy: 'AC Energy',
    ac_cost: 'AC Cost',
    shading_savings: 'Shading Savings',
    open_win_rec: 'Open Window Recommended! Outdoor air is cooler than indoor. Open window for free cooling!',
    close_cur_rec: 'Close Curtains Recommended! High solar radiation. Close curtains to reduce heat gain & save energy.',
    ms_unit: 'm/s',
    per_hour: '/ h',
    per_day: '/day',
    hour_short: 'h',
    min_short: 'min',
  },
  ru: {
    title: 'Thermal Balance',
    editor_title: 'Настройки Thermal Balance',
    instance_selector: 'Комната / Экземпляр (Автовыбор)',
    compact_view: 'Компактный режим (для смартфонов)',
    card_title_label: 'Свой заголовок карточки (опционально)',
    heat_gain_sensor: 'Сенсор притока тепла (Heat Gain)',
    ac_cooling_sensor: 'Сенсор отдачи AC (Cooling/Heating)',
    net_balance_sensor: 'Сенсор чистого баланса (Net Balance)',
    ac_cop_sensor: 'Сенсор эффективности AC (COP)',
    time_to_1c_sensor: 'Сенсор времени до ±1°C',
    daily_balance_sensor: 'Сенсор суточного баланса',
    total_balance_sensor: 'Сенсор общего баланса',
    heat_absorbed_sensor: 'Сенсор поглощенного тепла',
    ac_energy_sensor: 'Сенсор тепловой энергии AC',
    condensation_rate_sensor: 'Сенсор конденсата AC',
    empirical_k_factor_sensor: 'Сенсор факт. K-фактора (K-Factor)',
    ac_cost_sensor: 'Сенсор суточных затрат на AC',
    daily_savings_sensor: 'Сенсор экономии от штор',
    rec_open_window_sensor: 'Сенсор рекомендации открыть окно',
    rec_close_curtains_sensor: 'Сенсор рекомендации закрыть шторы',
    heat_mode: 'Режим Обогрева',
    cool_mode: 'Режим Охлаждения',
    stable: 'Баланс',
    heat_gain: 'Приток тепла',
    heat_loss: 'Теплопотери',
    ac_cooling: 'Охлаждение AC',
    ac_heating: 'Теплоотдача AC',
    net_balance: 'Чистый баланс',
    ventilation: 'Проветривание',
    to_1c: 'До ±1°C',
    condensation: 'Конденсат',
    vent_heat_exchange: 'Вентиляция и теплообмен',
    window: 'Окно',
    window_open: 'Открыто',
    window_closed: 'Закрыто',
    wind: 'Ветер',
    air_change: 'Кратность (ACH)',
    curtains: 'Шторы',
    curtains_closed: 'Закрыты',
    curtains_open: 'Открыты',
    curtains_note_no_sensor: 'Датчик освещенности не настроен',
    curtains_note_night: 'Ночь: автоопределение штор отключено',
    solar: 'Солнце',
    walls: 'Стены',
    k_factor_actual: 'K-фактор (факт)',
    insulation: 'Изоляция',
    estimated: 'Расчетная',
    grade_excellent: 'Отличная (по паспорту)',
    grade_good: 'Хорошая (умеренно)',
    grade_average: 'Средняя (мостики холода)',
    grade_poor: 'Слабая (сквозняки / утечки)',
    window_open_k_note: 'Окно открыто — K-фактор недостоверен',
    ac_cooling_perf: 'Характеристики охлаждения AC',
    heating_perf: 'Характеристики обогрева (ТН)',
    ac_dt: 'ΔT AC',
    exit_temp_meas: 'Темп. выдува (факт)',
    exit_temp: 'Темп. выдува',
    exit_temp_calc: 'Темп. выдува (расч.)',
    sensible_heat: 'Ощутимый холод',
    sensible_heat_heating: 'Ощутимое тепло',
    latent_heat: 'Скрытый холод (осушение)',
    shr: 'SHR (ощут./полн.)',
    enthalpy: 'Энтальпия',
    airflow: 'Расход воздуха',
    dew_point_in: 'Точка росы (комн.)',
    dew_point_out: 'Точка росы (ул.)',
    trend_24h: 'Суточный тренд баланса',
    heat: 'Приток',
    cooling: 'Холод',
    heating: 'Нагрев',
    net: 'Баланс',
    energy_cost_intel: 'Энергетические и финансовые счетчики',
    daily_balance: 'Суточный баланс',
    total_balance: 'Общий баланс',
    heat_absorbed: 'Поглощено тепла',
    ac_energy: 'Тепловая энергия AC',
    ac_cost: 'Затраты за день',
    shading_savings: 'Экономия от штор',
    open_win_rec: 'Рекомендуется открыть окно! На улице прохладнее, чем в комнате — используйте бесплатное охлаждение.',
    close_cur_rec: 'Рекомендуется закрыть шторы! Высокая солнечная радиация — зашторьте окна для экономии энергии.',
    ms_unit: 'м/с',
    per_hour: '/ ч',
    per_day: '/день',
    hour_short: 'ч',
    min_short: 'мин',
  }
};

const SENSOR_MAP = {
  heat_gain: ['_instant_heat_gain', '_heat_gain', '_solar_heat_gain'],
  ac_cooling: ['_ac_heat_output', '_ac_cooling', '_heat_output'],
  net_balance: ['_instant_net_balance', '_net_balance'],
  ac_cop: ['_ac_carnot_cop', '_ac_cop', '_carnot_cop'],
  time_to_1c: ['_time_to_1deg', '_time_to_1_c', '_time_to_1'],
  daily_balance: ['_daily_thermal_balance', '_daily_balance'],
  total_balance: ['_net_thermal_balance', '_total_balance'],
  heat_absorbed: ['_total_heat_absorbed', '_heat_absorbed'],
  ac_energy: ['_ac_thermal_energy_total', '_ac_energy'],
  condensation_rate: ['_ac_condensation_rate', '_condensation_rate'],
  empirical_k_factor: ['_empirical_k_factor', '_empirical_room_k_factor', '_k_factor'],
  ac_cost: ['_ac_energy_cost', '_energy_cost'],
  daily_savings: ['_shading_daily_savings', '_daily_savings'],
  rec_open_window: ['_recommend_open_window'],
  rec_close_curtains: ['_recommend_close_curtains'],
};

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function loadECharts() {
  if (window.echarts) return Promise.resolve(window.echarts);
  if (window._echartsLoadingPromise) return window._echartsLoadingPromise;

  window._echartsLoadingPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = '/thermal_balance/echarts.min.js';
    script.async = true;
    script.onload = () => resolve(window.echarts);
    script.onerror = () => {
      const script2 = document.createElement('script');
      script2.src = '/local/thermal_balance/echarts.min.js';
      script2.async = true;
      script2.onload = () => resolve(window.echarts);
      script2.onerror = (err) => reject(err);
      document.head.appendChild(script2);
    };
    document.head.appendChild(script);
  });
  return window._echartsLoadingPromise;
}

function autoDiscoverInstances(hass) {
  if (!hass || !hass.states) return [];
  const instances = [];
  const seen = new Set();
  const suffixes = SENSOR_MAP.heat_gain || ['_instant_heat_gain', '_heat_gain'];

  for (const eid of Object.keys(hass.states)) {
    const lower = eid.toLowerCase();
    if (!lower.startsWith('sensor.')) continue;

    for (const suf of suffixes) {
      if (lower.endsWith(suf)) {
        const withoutDomain = eid.substring('sensor.'.length);
        const prefix = withoutDomain.substring(0, withoutDomain.length - suf.length).replace(/^_|_$/g, '');
        if (!seen.has(prefix)) {
          seen.add(prefix);
          const stateObj = hass.states[eid];
          let name = prefix || 'Thermal Balance';
          if (stateObj && stateObj.attributes && stateObj.attributes.friendly_name) {
            const fn = stateObj.attributes.friendly_name;
            name = fn.replace(/(instant\s+heat\s+gain|heat\s+gain|приток\s+тепла)/gi, '').trim() || fn;
          }
          instances.push({ prefix, eid, name });
        }
        break;
      }
    }
  }
  return instances;
}

function derivePrefixFromEntity(eid) {
  if (!eid || typeof eid !== 'string') return null;
  const match = eid.replace(/^(sensor|binary_sensor)\./, '');
  for (const suffixes of Object.values(SENSOR_MAP)) {
    for (const suf of suffixes) {
      if (match.endsWith(suf)) {
        return match.substring(0, match.length - suf.length).replace(/^_|_$/g, '');
      }
    }
  }
  return null;
}

function autoDiscoverEntities(hass, preferredPrefix = null) {
  if (!hass || !hass.states) return {};
  const discovered = {};
  const allSensors = Object.keys(hass.states).filter(eid => {
    const lower = eid.toLowerCase();
    return lower.startsWith('sensor.') || lower.startsWith('binary_sensor.');
  });

  let prefix = preferredPrefix;
  if (prefix === null || prefix === undefined || prefix === '') {
    const instances = autoDiscoverInstances(hass);
    if (instances.length > 0) {
      prefix = instances[0].prefix;
    }
  }

  const prefixLower = prefix ? prefix.toLowerCase() : null;

  for (const [key, suffixes] of Object.entries(SENSOR_MAP)) {
    let matchedEid = null;

    if (prefixLower) {
      for (const eid of allSensors) {
        const lower = eid.toLowerCase();
        if (lower.includes(prefixLower) && suffixes.some(suf => lower.endsWith(suf) || lower.includes(suf))) {
          matchedEid = eid;
          break;
        }
      }
    }

    if (!matchedEid) {
      for (const eid of allSensors) {
        const lower = eid.toLowerCase();
        if (suffixes.some(suf => lower.endsWith(suf) || lower.includes(suf))) {
          matchedEid = eid;
          break;
        }
      }
    }

    if (matchedEid) {
      discovered[key] = matchedEid;
    }
  }
  return discovered;
}

/* ─────────────────────────────────────────────────────────────
 * VISUAL UI EDITOR CLASS
 * ───────────────────────────────────────────────────────────── */

class ThermalBalanceCardEditor extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = null;
    this._rendered = false;
    this._isSelfUpdating = false;
  }

  setConfig(config) {
    const isFirst = !this._rendered;
    const oldConfigStr = JSON.stringify(this._config || {});
    const newConfigStr = JSON.stringify(config || {});
    this._config = { ...config };

    if (this._isSelfUpdating) {
      this._isSelfUpdating = false;
      return;
    }

    if (isFirst || oldConfigStr !== newConfigStr) {
      this.render();
    }
  }

  set hass(hass) {
    const oldStates = this._hass && this._hass.states;
    this._hass = hass;
    if (!this._rendered) {
      this.render();
      return;
    }
    const newStates = hass && hass.states;
    if (oldStates && newStates) {
      const oldCount = Object.keys(oldStates).length;
      const newCount = Object.keys(newStates).length;
      if (oldCount !== newCount) {
        this.render();
      }
    }
  }

  connectedCallback() {
    if (!this._rendered) {
      this.render();
    }
  }

  _t(key, defaultText = '') {
    const lang = (this._hass && (this._hass.locale?.language || this._hass.language)) || 'en';
    const langCode = lang.toLowerCase().startsWith('ru') ? 'ru' : 'en';
    return (TRANSLATIONS[langCode] && TRANSLATIONS[langCode][key]) || (TRANSLATIONS.en && TRANSLATIONS.en[key]) || defaultText || key;
  }

  _valueChanged(ev) {
    if (!this._config) return;
    const target = ev.target;
    const configKey = target.getAttribute('configValue');
    if (!configKey) return;

    let newValue = ev.detail ? ev.detail.value : (target.type === 'checkbox' ? target.checked : target.value);
    if (this._config[configKey] === newValue) return;

    const newConfig = { ...this._config };
    if (newValue === '' || newValue === undefined) {
      delete newConfig[configKey];
    } else {
      newConfig[configKey] = newValue;
    }

    this._config = newConfig;
    this._isSelfUpdating = true;

    if (configKey === 'prefix' || configKey === 'room_prefix') {
      this._isSelfUpdating = false;
      this.render();
    }

    const event = new CustomEvent('config-changed', {
      detail: { config: this._config },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }

  render() {
    this._rendered = true;
    const active = this.shadowRoot ? this.shadowRoot.activeElement : null;
    const activeKey = active ? active.getAttribute('configValue') : null;
    const selStart = active && typeof active.selectionStart === 'number' ? active.selectionStart : null;
    const selEnd = active && typeof active.selectionEnd === 'number' ? active.selectionEnd : null;

    const instances = autoDiscoverInstances(this._hass);
    const selectedPrefix = this._config.prefix || this._config.room_prefix || '';
    const autoPrefix = instances.length > 0 ? instances[0].prefix : '';
    const activePrefix = selectedPrefix || autoPrefix;
    const auto = autoDiscoverEntities(this._hass, activePrefix);

    const fields = [
      { key: 'heat_gain', label: this._t('heat_gain_sensor') },
      { key: 'ac_cooling', label: this._t('ac_cooling_sensor') },
      { key: 'net_balance', label: this._t('net_balance_sensor') },
      { key: 'ac_cop', label: this._t('ac_cop_sensor') },
      { key: 'time_to_1c', label: this._t('time_to_1c_sensor') },
      { key: 'daily_balance', label: this._t('daily_balance_sensor') },
      { key: 'total_balance', label: this._t('total_balance_sensor') },
      { key: 'heat_absorbed', label: this._t('heat_absorbed_sensor') },
      { key: 'ac_energy', label: this._t('ac_energy_sensor') },
      { key: 'condensation_rate', label: this._t('condensation_rate_sensor') },
      { key: 'empirical_k_factor', label: this._t('empirical_k_factor_sensor') },
      { key: 'ac_cost', label: this._t('ac_cost_sensor') },
      { key: 'daily_savings', label: this._t('daily_savings_sensor') },
      { key: 'rec_open_window', label: this._t('rec_open_window_sensor') },
      { key: 'rec_close_curtains', label: this._t('rec_close_curtains_sensor') },
    ];

    const sensorEntities = (this._hass && this._hass.states)
      ? Object.keys(this._hass.states)
          .filter(e => e.startsWith('sensor.') || e.startsWith('binary_sensor.'))
          .map(eid => {
            const stateObj = this._hass.states[eid];
            const fname = (stateObj && stateObj.attributes && stateObj.attributes.friendly_name);
            const name = fname ? `${fname} (${eid})` : eid;
            return { eid, name };
          })
          .sort((a, b) => a.name.localeCompare(b.name))
      : [];

    const getAutoLabel = (key) => {
      const eid = auto[key];
      if (!eid) return 'None';
      const stateObj = this._hass && this._hass.states && this._hass.states[eid];
      const fname = stateObj && stateObj.attributes && stateObj.attributes.friendly_name;
      return fname ? `${fname} (${eid})` : eid;
    };

    const isCompact = Boolean(this._config.compact || this._config.compact_view);

    const fieldsHtml = fields.map(f => {
      const currentVal = this._config[f.key] || '';
      const autoLabel = getAutoLabel(f.key);

      const options = [
        `<option value="" ${currentVal === '' ? 'selected' : ''}>Auto (${escapeHtml(autoLabel)})</option>`,
        ...sensorEntities.map(e =>
          `<option value="${escapeHtml(e.eid)}" ${currentVal === e.eid ? 'selected' : ''}>${escapeHtml(e.name)}</option>`
        )
      ].join('');

      return `
        <div class="editor-row">
          <label class="editor-label">${escapeHtml(f.label)}</label>
          <select class="editor-select" configValue="${escapeHtml(f.key)}">
            ${options}
          </select>
        </div>
      `;
    }).join('');

    const instanceOptions = [
      `<option value="" ${selectedPrefix === '' ? 'selected' : ''}>Auto (${escapeHtml(instances.length > 0 ? (instances[0].name || instances[0].prefix) : 'Default')})</option>`,
      ...instances.map(inst =>
        `<option value="${escapeHtml(inst.prefix)}" ${selectedPrefix === inst.prefix ? 'selected' : ''}>${escapeHtml(inst.name)} (${escapeHtml(inst.prefix)})</option>`
      )
    ].join('');

    this.shadowRoot.innerHTML = `
      <style>
        .editor-container {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding: 8px 0;
          font-family: inherit;
        }
        .editor-title {
          font-size: 15px;
          font-weight: 700;
          color: var(--primary-text-color, #FFF);
          margin-bottom: 4px;
        }
        .editor-row {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .editor-row-inline {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 6px 0;
          border-bottom: 1px solid var(--divider-color, #233045);
        }
        .editor-label {
          font-size: 12.5px;
          font-weight: 500;
          color: var(--secondary-text-color, #9CA3AF);
        }
        .editor-select, .editor-input {
          background: var(--card-background-color, #162032);
          color: var(--primary-text-color, #FFF);
          border: 1px solid var(--divider-color, #233045);
          border-radius: 6px;
          padding: 8px 10px;
          font-size: 13px;
          font-family: inherit;
          width: 100%;
          box-sizing: border-box;
        }
        .editor-select:focus, .editor-input:focus {
          outline: none;
          border-color: var(--primary-color, #03a9f4);
        }
        .editor-checkbox {
          width: 18px;
          height: 18px;
          cursor: pointer;
        }
      </style>
      <div class="editor-container">
        <div class="editor-title">${this._t('editor_title')}</div>
        
        <div class="editor-row-inline">
          <label class="editor-label" style="font-weight: 600; color: var(--primary-text-color, #FFF);">${this._t('compact_view')}</label>
          <input type="checkbox" class="editor-checkbox" configValue="compact" ${isCompact ? 'checked' : ''}/>
        </div>

        <div class="editor-row">
          <label class="editor-label">${this._t('card_title_label')}</label>
          <input type="text" class="editor-input" configValue="title" value="${escapeHtml(this._config.title || '')}" placeholder="Thermal Balance"/>
        </div>

        ${instances.length > 0 ? `
        <div class="editor-row">
          <label class="editor-label">${this._t('instance_selector')}</label>
          <select class="editor-select" configValue="prefix">
            ${instanceOptions}
          </select>
        </div>` : ''}

        ${fieldsHtml}
      </div>
    `;

    const selects = this.shadowRoot.querySelectorAll('.editor-select, .editor-input, .editor-checkbox');
    selects.forEach(s => {
      s.addEventListener('change', this._valueChanged.bind(this));
      if (s.tagName === 'INPUT' && s.type === 'text') {
        s.addEventListener('input', this._valueChanged.bind(this));
      }
    });

    if (activeKey) {
      const newActive = this.shadowRoot.querySelector(`[configValue="${activeKey}"]`);
      if (newActive) {
        newActive.focus();
        if (selStart !== null && typeof newActive.setSelectionRange === 'function') {
          newActive.setSelectionRange(selStart, selEnd);
        }
      }
    }
  }
}

if (!customElements.get('thermal-balance-card-editor')) {
  customElements.define('thermal-balance-card-editor', ThermalBalanceCardEditor);
}

/* ─────────────────────────────────────────────────────────────
 * MAIN LOVELACE CARD CLASS
 * ───────────────────────────────────────────────────────────── */

class ThermalBalanceCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._hass = null;
    this._config = {};
    this._lastHash = '';
    this._chart = null;
    this._resizeObserver = null;
    this._onWindowResize = null;
    this._scaffoldCreated = false;
    this._els = {};
  }

  static getConfigElement() {
    return document.createElement('thermal-balance-card-editor');
  }

  static getStubConfig(hass) {
    const instances = autoDiscoverInstances(hass);
    const prefix = instances.length > 0 ? instances[0].prefix : null;
    return autoDiscoverEntities(hass, prefix);
  }

  static getGridOptions(hass, config) {
    const isCompact = Boolean(config && (config.compact || config.compact_view));
    return {
      columns: 12,
      rows: isCompact ? 4 : 6,
      min_columns: 6,
      min_rows: isCompact ? 3 : 4,
    };
  }

  getGridOptions() {
    const isCompact = Boolean(this._config && (this._config.compact || this._config.compact_view));
    return {
      columns: 12,
      rows: isCompact ? 4 : 6,
      min_columns: 6,
      min_rows: isCompact ? 3 : 4,
    };
  }

  setConfig(config) {
    if (!config) throw new Error('Invalid configuration');
    this._config = { ...config };
    this._lastHash = '';
    this._lastHistoryFetch = 0;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  connectedCallback() {
    if (!this._onWindowResize) {
      this._onWindowResize = () => {
        if (this._chart && !this._chart.isDisposed()) {
          this._chart.resize();
        }
      };
      window.addEventListener('resize', this._onWindowResize);
    }
    this._lastHash = '';
    this._render();
  }

  disconnectedCallback() {
    if (this._resizeObserver) {
      this._resizeObserver.disconnect();
      this._resizeObserver = null;
    }
    if (this._onWindowResize) {
      window.removeEventListener('resize', this._onWindowResize);
      this._onWindowResize = null;
    }
    if (this._chart && !this._chart.isDisposed()) {
      try {
        this._chart.dispose();
      } catch (e) {}
      this._chart = null;
    }
    this._scaffoldCreated = false;
    this._els = null;
    this._lastHash = '';
  }

  _setupResizeObserver() {
    if (this._resizeObserver) return;
    const container = this.shadowRoot ? this.shadowRoot.querySelector('.tb-card') : null;
    if (!container || typeof ResizeObserver === 'undefined') return;

    this._resizeObserver = new ResizeObserver(() => {
      if (this._chart && !this._chart.isDisposed()) {
        this._chart.resize();
      }
    });
    this._resizeObserver.observe(container);
  }

  getCardSize() {
    return (this._config && (this._config.compact || this._config.compact_view)) ? 4 : 6;
  }

  _t(key, defaultText = '') {
    const lang = (this._hass && (this._hass.locale?.language || this._hass.language)) || 'en';
    const langCode = lang.toLowerCase().startsWith('ru') ? 'ru' : 'en';
    return (TRANSLATIONS[langCode] && TRANSLATIONS[langCode][key]) || (TRANSLATIONS.en && TRANSLATIONS.en[key]) || defaultText || key;
  }

  _translateGrade(grade) {
    if (!grade) return this._t('estimated');
    const lower = String(grade).toLowerCase();
    if (lower.includes('excellent')) return this._t('grade_excellent', grade);
    if (lower.includes('good')) return this._t('grade_good', grade);
    if (lower.includes('average')) return this._t('grade_average', grade);
    if (lower.includes('poor')) return this._t('grade_poor', grade);
    return grade;
  }

  _translateCurtainsNote(note) {
    if (!note) return '';
    const lower = String(note).toLowerCase();
    if (lower.includes('not configured')) return this._t('curtains_note_no_sensor', note);
    if (lower.includes('night')) return this._t('curtains_note_night', note);
    return note;
  }

  /* ─── Helpers for Entity Resolution ─── */

  _derivePrefix() {
    if (this._config && (this._config.prefix || this._config.room_prefix)) {
      return this._config.prefix || this._config.room_prefix;
    }
    if (this._config && this._config.heat_gain) {
      return derivePrefixFromEntity(this._config.heat_gain);
    }
    return null;
  }

  _resolveEntity(key) {
    if (this._config && this._config[key]) return this._config[key];
    const prefix = this._derivePrefix();
    if (!this._autoDiscovered || this._autoDiscoveredPrefix !== prefix) {
      this._autoDiscovered = autoDiscoverEntities(this._hass, prefix);
      this._autoDiscoveredPrefix = prefix;
    }
    return this._autoDiscovered ? this._autoDiscovered[key] : null;
  }

  _getState(key) {
    const eid = this._resolveEntity(key);
    if (!eid || !this._hass || !this._hass.states) return null;
    const s = this._hass.states[eid];
    if (!s || s.state === 'unavailable' || s.state === 'unknown') return null;
    return parseFloat(s.state);
  }

  _getBoolState(key) {
    const eid = this._resolveEntity(key);
    if (!eid || !this._hass || !this._hass.states) return null;
    const s = this._hass.states[eid];
    if (!s || s.state === 'unavailable' || s.state === 'unknown') return null;
    return s.state === 'on' || s.state === 'true' || s.state === '1' || s.state === 1;
  }

  _getAttr(key, attr) {
    const eid = this._resolveEntity(key);
    if (!eid || !this._hass || !this._hass.states) return null;
    const s = this._hass.states[eid];
    if (!s || !s.attributes) return null;
    const v = s.attributes[attr];
    return v === undefined ? null : v;
  }

  _fmt(v, decimals = 0) {
    if (v === null || v === undefined || isNaN(v)) return '—';
    return Number(v).toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }

  _fmtTime(val, direction) {
    if (val === null || val === undefined) return '—';
    const m = Math.round(val);
    if (m === 0 && direction === 'equilibrium') return this._t('stable');
    if (m >= 60) {
      const h = Math.floor(m / 60);
      const rm = m % 60;
      return rm > 0 ? `${h}${this._t('hour_short')} ${rm}${this._t('min_short')}` : `${h}${this._t('hour_short')}`;
    }
    return `${m} ${this._t('min_short')}`;
  }

  _balanceColor(v) {
    if (v === null || v === undefined || isNaN(v)) return '#00C896';
    if (v > 50) return '#FF7A3C';
    if (v < -50) return '#4DA3FF';
    return '#00C896';
  }

  _balanceBg(v) {
    if (v === null || v === undefined || isNaN(v)) return 'rgba(0, 200, 150, 0.15)';
    if (v > 50) return 'rgba(255, 122, 60, 0.15)';
    if (v < -50) return 'rgba(77, 163, 255, 0.15)';
    return 'rgba(0, 200, 150, 0.15)';
  }

  _dirIcon(dir) {
    if (dir === 'heating') return { sym: '▲', color: '#FF7A3C' };
    if (dir === 'cooling') return { sym: '▼', color: '#4DA3FF' };
    return { sym: '⚖', color: '#00C896' };
  }

  /* ─── SVG Gauge ─── */

  _gauge(value, max, color1, color2, label, iconSvg) {
    const r = 55;
    const circumference = Math.PI * r;
    const pct = Math.min(1, Math.max(0, Math.abs(value || 0) / max));
    const offset = circumference * (1 - pct);
    const display = value !== null ? this._fmt(value, 0) : '—';
    const gradId = `grad-${label.replace(/[^a-zA-Z0-9]/g, '')}`;

    return `
      <div class="gauge-card" role="group" aria-label="${escapeHtml(label)}: ${display} W">
        <svg viewBox="0 0 140 85" class="gauge-svg" role="img" aria-label="${escapeHtml(label)}: ${display} W">
          <defs>
            <linearGradient id="${gradId}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="${color1}"/>
              <stop offset="100%" stop-color="${color2}"/>
            </linearGradient>
          </defs>
          <path d="M 15 72 A 55 55 0 0 1 125 72"
                fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="8" stroke-linecap="round" aria-hidden="true"/>
          <path d="M 15 72 A 55 55 0 0 1 125 72"
                fill="none" stroke="url(#${gradId})" stroke-width="8" stroke-linecap="round"
                stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
                style="transition: stroke-dashoffset 0.8s ease" aria-hidden="true"/>
          <text x="70" y="58" text-anchor="middle" fill="#E5E7EB" font-size="22" font-weight="700" font-family="inherit">${display}</text>
          <text x="70" y="74" text-anchor="middle" fill="#9CA3AF" font-size="11" font-weight="600" font-family="inherit">W</text>
        </svg>
        <div class="gauge-label">
          <span class="gauge-icon" aria-hidden="true">${iconSvg}</span>
          <span>${escapeHtml(label)}</span>
        </div>
      </div>`;
  }

  get _icons() {
    return {
      sun: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FF7A3C" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`,
      fire: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FF7A3C" stroke-width="2" stroke-linecap="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>`,
      fireLg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FF7A3C" stroke-width="2" stroke-linecap="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>`,
      snowflake: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4DA3FF" stroke-width="2" stroke-linecap="round"><line x1="12" y1="2" x2="12" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="5.5" y1="5.5" x2="18.5" y2="18.5"/><line x1="18.5" y1="5.5" x2="5.5" y2="18.5"/><polyline points="8,2 12,6 16,2"/><polyline points="8,22 12,18 16,22"/><polyline points="2,8 6,12 2,16"/><polyline points="22,8 18,12 22,16"/></svg>`,
      snowflakeLg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4DA3FF" stroke-width="2" stroke-linecap="round"><line x1="12" y1="2" x2="12" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="5.5" y1="5.5" x2="18.5" y2="18.5"/><line x1="18.5" y1="5.5" x2="5.5" y2="18.5"/><polyline points="8,2 12,6 16,2"/><polyline points="8,22 12,18 16,22"/><polyline points="2,8 6,12 2,16"/><polyline points="22,8 18,12 22,16"/></svg>`,
      thermo: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>`,
      bolt: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FACC15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
      trend: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FF7A3C" stroke-width="2" stroke-linecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
    };
  }

  /* ─── 24h History Trend Sparkline ─── */

  _fetchHistory() {
    if (!this._hass || this._fetchingHistory) return;
    const now = Date.now();
    if (this._lastHistoryFetch && (now - this._lastHistoryFetch < 300000)) return;
    this._fetchingHistory = true;
    this._lastHistoryFetch = now;

    const heatEid = this._resolveEntity('heat_gain');
    const coolEid = this._resolveEntity('ac_cooling');
    const netEid = this._resolveEntity('net_balance');
    if (!heatEid && !coolEid && !netEid) {
      this._fetchingHistory = false;
      return;
    }

    const entityIds = [heatEid, coolEid, netEid].filter(Boolean);
    const startTime = new Date(now - 24 * 3600 * 1000).toISOString();

    this._hass.callWS({
      type: 'history/history_during_period',
      start_time: startTime,
      entity_ids: entityIds,
      no_attributes: true,
      minimal_response: true,
    }).then(res => {
      this._fetchingHistory = false;
      this._historyData = res || {};
      this._historyVersion = (this._historyVersion || 0) + 1;
      this._lastHash = '';
      const isHeating = Boolean(this._getAttr('ac_cooling', 'is_heating') || this._getAttr('net_balance', 'is_heating'));
      this._initEChart(isHeating);
    }).catch(err => {
      this._fetchingHistory = false;
      console.warn('ThermalBalanceCard: failed to fetch history', err);
    });
  }

  _sampleHistory(key, liveVal, numPoints = 288) {
    const eid = this._resolveEntity(key);
    const validLive = (liveVal !== null && liveVal !== undefined && !isNaN(liveVal)) ? parseFloat(liveVal) : 0;
    const result = new Array(numPoints).fill(validLive);

    if (!eid || !this._historyData || !this._historyData[eid]) {
      return result;
    }

    const items = this._historyData[eid];
    if (!Array.isArray(items) || items.length === 0) {
      return result;
    }

    const now = Date.now() / 1000;
    const start = now - 86400;
    const interval = 86400 / (numPoints - 1);

    const firstRaw = items[0].s !== undefined ? items[0].s : items[0].state;
    let firstVal = parseFloat(firstRaw);
    let currentVal = !isNaN(firstVal) ? firstVal : validLive;
    let itemIdx = 0;

    for (let i = 0; i < numPoints; i++) {
      const targetTime = start + (i * interval);

      while (itemIdx < items.length) {
        const item = items[itemIdx];
        const rawTime = item.lu !== undefined ? item.lu : (item.lc !== undefined ? item.lc : (item.last_updated ? new Date(item.last_updated).getTime() / 1000 : (item.last_changed ? new Date(item.last_changed).getTime() / 1000 : null)));
        if (rawTime === null || rawTime === undefined || isNaN(rawTime)) {
          itemIdx++;
          continue;
        }
        const itemTime = rawTime > 1e11 ? rawTime / 1000 : rawTime;
        if (itemTime <= targetTime) {
          const rawVal = item.s !== undefined ? item.s : item.state;
          const parsed = parseFloat(rawVal);
          if (!isNaN(parsed)) currentVal = parsed;
          itemIdx++;
        } else {
          break;
        }
      }
      result[i] = currentVal;
    }

    if (liveVal !== null && liveVal !== undefined && !isNaN(liveVal)) {
      result[numPoints - 1] = parseFloat(liveVal);
    }

    return result;
  }

  _smoothPoints(pts) {
    if (!pts || pts.length < 3) return pts;
    const len = pts.length;
    const smoothed = new Array(len);
    smoothed[0] = pts[0];
    for (let i = 1; i < len - 1; i++) {
      smoothed[i] = 0.20 * pts[i - 1] + 0.60 * pts[i] + 0.20 * pts[i + 1];
    }
    smoothed[len - 1] = pts[len - 1];
    return smoothed;
  }

  _getTrendPoints(key, liveVal, numPoints = 288) {
    const raw = this._sampleHistory(key, liveVal, numPoints);
    return this._smoothPoints(raw);
  }

  _pointsToPath(points, width, height, maxVal) {
    if (!points || points.length === 0) return '';
    const step = width / Math.max(1, points.length - 1);
    const maxY = maxVal > 0 ? maxVal : 100;

    const coords = points.map((val, idx) => {
      const x = idx * step;
      const y = height - (Math.min(maxY, Math.max(0, val)) / maxY) * (height - 8) - 4;
      return { x, y };
    });

    if (coords.length === 1) return `M 0 ${coords[0].y} L ${width} ${coords[0].y}`;

    let d = `M ${coords[0].x.toFixed(1)} ${coords[0].y.toFixed(1)}`;
    for (let i = 0; i < coords.length - 1; i++) {
      const p0 = coords[i];
      const p1 = coords[i + 1];
      const cp1x = (p0.x + (p1.x - p0.x) / 2).toFixed(1);
      const cp1y = p0.y.toFixed(1);
      const cp2x = cp1x;
      const cp2y = p1.y.toFixed(1);
      d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p1.x.toFixed(1)} ${p1.y.toFixed(1)}`;
    }
    return d;
  }

  _pointsToArea(points, width, height, maxVal) {
    const linePath = this._pointsToPath(points, width, height, maxVal);
    if (!linePath) return '';
    return `${linePath} L ${width} ${height} L 0 ${height} Z`;
  }

  _renderTrendSvg(heatPoints, coolPoints, isHeating = false) {
    const width = 300;
    const height = 65;
    const all = [...(heatPoints || []), ...(coolPoints || [])];
    const maxVal = Math.max(500, ...all);

    const heatLine = this._pointsToPath(heatPoints, width, height, maxVal);
    const heatArea = this._pointsToArea(heatPoints, width, height, maxVal);

    const coolLine = this._pointsToPath(coolPoints, width, height, maxVal);
    const coolArea = this._pointsToArea(coolPoints, width, height, maxVal);

    const hvacColor = isHeating ? '#FF7A3C' : '#4DA3FF';

    return `
      <svg viewBox="0 0 ${width} ${height}" class="trend-svg" preserveAspectRatio="none">
        <defs>
          <linearGradient id="heatTrendGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#FF7A3C" stop-opacity="0.35"/>
            <stop offset="100%" stop-color="#FF7A3C" stop-opacity="0.0"/>
          </linearGradient>
          <linearGradient id="coolTrendGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="${hvacColor}" stop-opacity="0.35"/>
            <stop offset="100%" stop-color="${hvacColor}" stop-opacity="0.0"/>
          </linearGradient>
        </defs>
        <!-- Grid lines -->
        <line x1="0" y1="15" x2="${width}" y2="15" stroke="#1C2538" stroke-dasharray="3 3"/>
        <line x1="0" y1="45" x2="${width}" y2="45" stroke="#1C2538" stroke-dasharray="3 3"/>

        ${heatArea ? `<path d="${heatArea}" fill="url(#heatTrendGrad)"/>` : ''}
        ${coolArea ? `<path d="${coolArea}" fill="url(#coolTrendGrad)"/>` : ''}
        ${heatLine ? `<path d="${heatLine}" fill="none" stroke="#FF7A3C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>` : ''}
        ${coolLine ? `<path d="${coolLine}" fill="none" stroke="${hvacColor}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>` : ''}
      </svg>
    `;
  }

  _initEChart(isHeating = false) {
    const container = this.shadowRoot ? this.shadowRoot.querySelector('#echart-container') : null;
    if (!container) return;

    loadECharts().then(echarts => {
      if (!this.shadowRoot) return;
      const currentContainer = this.shadowRoot.querySelector('#echart-container');
      if (!currentContainer) return;

      const existingChart = echarts.getInstanceByDom(currentContainer);
      if (!this._chart || this._chart.isDisposed() || existingChart !== this._chart) {
        if (this._chart && !this._chart.isDisposed()) {
          try { this._chart.dispose(); } catch(e){}
        }
        this._chart = echarts.init(currentContainer, null, { renderer: 'canvas' });
      }

      const numPoints = 288;
      const heatPoints = this._getTrendPoints('heat_gain', this._getState('heat_gain'), numPoints);
      const coolPoints = this._getTrendPoints('ac_cooling', this._getState('ac_cooling'), numPoints);
      const netPoints = this._getTrendPoints('net_balance', this._getState('net_balance'), numPoints);

      const nowMs = Date.now();
      const startMs = nowMs - 86400000;
      const intervalMs = 86400000 / (numPoints - 1);

      const timeLabels = Array.from({ length: numPoints }, (_, i) => {
        const ptTime = new Date(startMs + i * intervalMs);
        const hh = ptTime.getHours().toString().padStart(2, '0');
        const mm = ptTime.getMinutes().toString().padStart(2, '0');
        return `${hh}:${mm}`;
      });

      const hvacSeriesName = isHeating ? this._t('heating') : this._t('cooling');
      const hvacColor = isHeating ? '#FF7A3C' : '#4DA3FF';
      const hvacGradAlpha = isHeating ? 'rgba(255, 122, 60, 0.25)' : 'rgba(77, 163, 255, 0.25)';

      const option = {
        backgroundColor: 'transparent',
        legend: {
          show: true,
          top: 0,
          right: 8,
          textStyle: { color: '#9CA3AF', fontSize: 11, fontWeight: 500 },
          icon: 'roundRect',
          itemWidth: 12,
          itemHeight: 4,
          data: [this._t('heat'), hvacSeriesName, this._t('net')]
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: '#121A2B',
          borderColor: '#233045',
          borderWidth: 1,
          padding: [8, 12],
          textStyle: { color: '#E5E7EB', fontSize: 11 },
          formatter: (params) => {
            let res = `<div style="font-weight:600;margin-bottom:4px;color:#D1D5DB">${params[0].name}</div>`;
            params.forEach(p => {
              const sign = p.value > 0 ? '+' : '';
              res += `<div style="display:flex;align-items:center;gap:6px;margin-top:2px">
                        <span style="width:8px;height:8px;border-radius:50%;background:${p.color}"></span>
                        <span>${p.seriesName}: <b style="color:#FFF">${sign}${Math.round(p.value)} W</b></span>
                      </div>`;
            });
            return res;
          }
        },
        grid: {
          top: 26,
          right: 12,
          bottom: 22,
          left: 48,
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: timeLabels,
          axisLine: { lineStyle: { color: '#233045' } },
          axisLabel: { color: '#9CA3AF', fontSize: 10, interval: 35 },
          splitLine: { show: false }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          axisLabel: { color: '#9CA3AF', fontSize: 10, formatter: '{value} W' },
          splitLine: { lineStyle: { color: '#1C2538' } }
        },
        series: [
          {
            name: this._t('heat'),
            type: 'line',
            smooth: 0.3,
            smoothMonotone: 'x',
            sampling: 'lttb',
            showSymbol: false,
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: { color: '#FF7A3C' },
            lineStyle: { width: 2.0, color: '#FF7A3C' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(255, 122, 60, 0.25)' },
                { offset: 1, color: 'rgba(255, 122, 60, 0.0)' }
              ])
            },
            data: heatPoints.map(v => Math.round(v))
          },
          {
            name: hvacSeriesName,
            type: 'line',
            smooth: 0.3,
            smoothMonotone: 'x',
            sampling: 'lttb',
            showSymbol: false,
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: { color: hvacColor },
            lineStyle: { width: 2.0, color: hvacColor },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: hvacGradAlpha },
                { offset: 1, color: 'rgba(0, 0, 0, 0.0)' }
              ])
            },
            data: coolPoints.map(v => Math.round(v))
          },
          {
            name: this._t('net'),
            type: 'line',
            smooth: 0.3,
            smoothMonotone: 'x',
            sampling: 'lttb',
            showSymbol: false,
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: { color: '#00C896' },
            lineStyle: { width: 2.2, color: '#00C896', type: 'dashed' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(0, 200, 150, 0.12)' },
                { offset: 1, color: 'rgba(0, 200, 150, 0.0)' }
              ])
            },
            data: netPoints.map(v => Math.round(v))
          }
        ]
      };

      this._chart.setOption(option, true);
      setTimeout(() => this._chart && this._chart.resize(), 50);
    }).catch(() => {});
  }

  /* ─── Render ─── */

  _createScaffold() {
    this.shadowRoot.innerHTML = `
      <style>${this._css()}</style>
      <ha-card id="tb-ha-card" class="cooling-theme">
        <div class="tb-card">
          <div id="tb-advice-container" role="region" aria-live="polite" aria-atomic="true"></div>
          <div class="card-layout">
            <!-- COLUMN 1 -->
            <div class="card-col col-left">
              <!-- HEADER -->
              <div class="header">
                <div class="header-left">
                  <div class="header-icon" aria-hidden="true">${this._icons.thermo}</div>
                  <div class="header-text">
                    <div class="header-title" id="tb-header-title">Thermal Balance</div>
                    <div class="header-sub" id="tb-header-sub"></div>
                  </div>
                </div>
                <div class="header-badge" id="tb-header-badge" role="status" style="background:var(--tb-theme-badge-bg); color:var(--tb-theme-accent); border:1px solid var(--tb-theme-border);">
                  — W
                </div>
              </div>

              <!-- GAUGES -->
              <div class="gauges-row">
                <div class="gauge-card" role="group" aria-labelledby="tb-gauge-heat-label">
                  <svg viewBox="0 0 140 85" class="gauge-svg" role="img" id="tb-gauge-heat-svg" aria-label="Heat Gain: — W">
                    <defs>
                      <linearGradient id="tb-grad-heat" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop id="tb-grad-heat-stop1" offset="0%" stop-color="#FF7A3C"/>
                        <stop id="tb-grad-heat-stop2" offset="100%" stop-color="#FFB199"/>
                      </linearGradient>
                    </defs>
                    <path d="M 15 72 A 55 55 0 0 1 125 72" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="8" stroke-linecap="round" aria-hidden="true"/>
                    <path id="tb-gauge-heat-path" d="M 15 72 A 55 55 0 0 1 125 72" fill="none" stroke="url(#tb-grad-heat)" stroke-width="8" stroke-linecap="round" stroke-dasharray="172.7876" stroke-dashoffset="172.7876" style="transition: stroke-dashoffset 0.8s ease" aria-hidden="true"/>
                    <text id="tb-gauge-heat-val" x="70" y="58" text-anchor="middle" fill="#E5E7EB" font-size="22" font-weight="700" font-family="inherit">—</text>
                    <text x="70" y="74" text-anchor="middle" fill="#9CA3AF" font-size="11" font-weight="600" font-family="inherit">W</text>
                  </svg>
                  <div class="gauge-label" id="tb-gauge-heat-label">
                    <span class="gauge-icon" id="tb-gauge-heat-icon" aria-hidden="true">${this._icons.sun}</span>
                    <span id="tb-gauge-heat-label-text"></span>
                  </div>
                </div>

                <div class="gauge-card" role="group" aria-labelledby="tb-gauge-ac-label">
                  <svg viewBox="0 0 140 85" class="gauge-svg" role="img" id="tb-gauge-ac-svg" aria-label="AC Cooling: — W">
                    <defs>
                      <linearGradient id="tb-grad-ac" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop id="tb-grad-ac-stop1" offset="0%" stop-color="#4DA3FF"/>
                        <stop id="tb-grad-ac-stop2" offset="100%" stop-color="#93C5FD"/>
                      </linearGradient>
                    </defs>
                    <path d="M 15 72 A 55 55 0 0 1 125 72" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="8" stroke-linecap="round" aria-hidden="true"/>
                    <path id="tb-gauge-ac-path" d="M 15 72 A 55 55 0 0 1 125 72" fill="none" stroke="url(#tb-grad-ac)" stroke-width="8" stroke-linecap="round" stroke-dasharray="172.7876" stroke-dashoffset="172.7876" style="transition: stroke-dashoffset 0.8s ease" aria-hidden="true"/>
                    <text id="tb-gauge-ac-val" x="70" y="58" text-anchor="middle" fill="#E5E7EB" font-size="22" font-weight="700" font-family="inherit">—</text>
                    <text x="70" y="74" text-anchor="middle" fill="#9CA3AF" font-size="11" font-weight="600" font-family="inherit">W</text>
                  </svg>
                  <div class="gauge-label" id="tb-gauge-ac-label">
                    <span class="gauge-icon" id="tb-gauge-ac-icon" aria-hidden="true">${this._icons.snowflake}</span>
                    <span id="tb-gauge-ac-label-text"></span>
                  </div>
                </div>
              </div>

              <!-- METRICS BAR -->
              <div class="metrics-bar" role="list">
                <div class="metric-block" role="listitem" id="tb-metric-net-block">
                  <div class="metric-icon" style="color:var(--tb-theme-accent)" aria-hidden="true">⚡</div>
                  <div class="metric-val" id="tb-metric-net-val" style="color:var(--tb-theme-accent)">— <span class="metric-unit">W</span></div>
                  <div class="metric-label" id="tb-metric-net-lbl"></div>
                </div>
                <div class="metric-block" role="listitem" id="tb-metric-vent-block">
                  <div class="metric-icon" id="tb-metric-vent-icon" aria-hidden="true">🪟</div>
                  <div class="metric-val" id="tb-metric-vent-val">—</div>
                  <div class="metric-label" id="tb-metric-vent-lbl"></div>
                </div>
                <div class="metric-block" role="listitem" id="tb-metric-time-block">
                  <div class="metric-icon" id="tb-metric-time-icon" style="color:#FACC15" aria-hidden="true">⚖</div>
                  <div class="metric-val" id="tb-metric-time-val" style="color:#FACC15">—</div>
                  <div class="metric-label" id="tb-metric-time-lbl"></div>
                </div>
                <div class="metric-block" role="listitem" id="tb-metric-cond-block">
                  <div class="metric-icon" style="color:#93C5FD" aria-hidden="true">💧</div>
                  <div class="metric-val" id="tb-metric-cond-val" style="color:#93C5FD">— <span class="metric-unit">L/h</span></div>
                  <div class="metric-label" id="tb-metric-cond-lbl"></div>
                </div>
              </div>

              <!-- VENTILATION & THERMAL SOURCES -->
              <div class="section">
                <div class="section-title">🪟 <span id="tb-sec-vent-title"></span></div>
                <div class="ac-grid" id="tb-sec-vent-grid">
                  <div class="ac-row">
                    <span class="ac-dot" id="tb-vrow-win-dot"></span>
                    <span class="ac-label" id="tb-vrow-win-lbl"></span>
                    <span class="ac-val" id="tb-vrow-win-val"></span>
                  </div>
                  <div class="ac-row">
                    <span class="ac-dot" id="tb-vrow-vent-dot"></span>
                    <span class="ac-label" id="tb-vrow-vent-lbl"></span>
                    <span class="ac-val" id="tb-vrow-vent-val"></span>
                  </div>
                  <div class="ac-row" id="tb-vrow-wind-row" style="display:none">
                    <span class="ac-dot" style="background:#60A5FA"></span>
                    <span class="ac-label" id="tb-vrow-wind-lbl"></span>
                    <span class="ac-val" id="tb-vrow-wind-val" style="color:#60A5FA"></span>
                  </div>
                  <div class="ac-row" id="tb-vrow-ach-row" style="display:none">
                    <span class="ac-dot" style="background:#34D399"></span>
                    <span class="ac-label" id="tb-vrow-ach-lbl"></span>
                    <span class="ac-val" id="tb-vrow-ach-val" style="color:#34D399"></span>
                  </div>
                  <div class="ac-row" id="tb-vrow-curtains-row" style="display:none">
                    <span class="ac-dot" id="tb-vrow-curtains-dot"></span>
                    <span class="ac-label" id="tb-vrow-curtains-lbl"></span>
                    <span class="ac-val" id="tb-vrow-curtains-val"></span>
                  </div>
                  <div class="curtains-note" id="tb-vrow-curtains-note" style="display:none"></div>
                  <div class="ac-row">
                    <span class="ac-dot" style="background:#FACC15"></span>
                    <span class="ac-label" id="tb-vrow-solar-lbl"></span>
                    <span class="ac-val" id="tb-vrow-solar-val"></span>
                  </div>
                  <div class="ac-row">
                    <span class="ac-dot" style="background:#8B5CF6"></span>
                    <span class="ac-label" id="tb-vrow-wall-lbl"></span>
                    <span class="ac-val" id="tb-vrow-wall-val"></span>
                  </div>
                  <div class="ac-row">
                    <span class="ac-dot" style="background:#00C896"></span>
                    <span class="ac-label" id="tb-vrow-k-lbl"></span>
                    <span class="ac-val" id="tb-vrow-k-val" style="color:#00C896"></span>
                  </div>
                  <div class="ac-row">
                    <span class="ac-dot" style="background:#3B82F6"></span>
                    <span class="ac-label" id="tb-vrow-insul-lbl"></span>
                    <span class="ac-val" id="tb-vrow-insul-val" style="font-size: 0.85em; color: #9CA3AF;"></span>
                  </div>
                  <div class="curtains-note" id="tb-vrow-win-k-note" style="display:none"></div>
                </div>
              </div>

              <!-- AC PERFORMANCE -->
              <div class="section">
                <div class="section-title"><span id="tb-sec-ac-icon"></span> <span id="tb-sec-ac-title"></span></div>
                <div class="ac-grid" id="tb-sec-ac-grid"></div>
              </div>
            </div>

            <!-- COLUMN 2 -->
            <div class="card-col col-right">
              <!-- 24H ECHARTS TREND -->
              <div class="section" style="flex: 1; display: flex; flex-direction: column;">
                <div class="section-title">
                  ${this._icons.trend}
                  <span id="tb-trend-title"></span>
                </div>
                <div id="echart-container" style="width: 100%; flex: 1; min-height: 150px; margin-top: 4px;"></div>
              </div>

              <!-- ENERGY & COSTS -->
              <div class="section">
                <div class="section-title">${this._icons.bolt} <span id="tb-sec-energy-title"></span></div>
                <div class="energy-grid" role="list">
                  <div class="energy-card" role="listitem">
                    <div class="energy-icon" id="tb-ecard-daily-icon" style="color:#00C896" aria-hidden="true">📅</div>
                    <div class="energy-val" id="tb-ecard-daily-val" style="color:#00C896">—</div>
                    <div class="energy-unit">kWh</div>
                    <div class="energy-label" id="tb-ecard-daily-lbl"></div>
                  </div>
                  <div class="energy-card" role="listitem">
                    <div class="energy-icon" style="color:#8B5CF6" aria-hidden="true">Σ</div>
                    <div class="energy-val" id="tb-ecard-total-val" style="color:#8B5CF6">—</div>
                    <div class="energy-unit">kWh</div>
                    <div class="energy-label" id="tb-ecard-total-lbl"></div>
                  </div>
                  <div class="energy-card" role="listitem">
                    <div class="energy-icon" style="color:#FF7A3C" aria-hidden="true">🔥</div>
                    <div class="energy-val" id="tb-ecard-heat-val" style="color:#FF7A3C">—</div>
                    <div class="energy-unit">kWh</div>
                    <div class="energy-label" id="tb-ecard-heat-lbl"></div>
                  </div>
                  <div class="energy-card" role="listitem">
                    <div class="energy-icon" id="tb-ecard-ac-icon" style="color:#4DA3FF" aria-hidden="true">❄</div>
                    <div class="energy-val" id="tb-ecard-ac-val" style="color:#4DA3FF">—</div>
                    <div class="energy-unit">kWh</div>
                    <div class="energy-label" id="tb-ecard-ac-lbl"></div>
                  </div>
                  <div class="energy-card" role="listitem">
                    <div class="energy-icon" style="color:#FACC15" aria-hidden="true">💰</div>
                    <div class="energy-val" id="tb-ecard-cost-val" style="color:#FACC15">—</div>
                    <div class="energy-unit" id="tb-ecard-cost-unit"></div>
                    <div class="energy-label" id="tb-ecard-cost-lbl"></div>
                  </div>
                  <div class="energy-card" role="listitem">
                    <div class="energy-icon" style="color:#00C896" aria-hidden="true">🌱</div>
                    <div class="energy-val" id="tb-ecard-shading-val" style="color:#00C896">—</div>
                    <div class="energy-unit" id="tb-ecard-shading-unit"></div>
                    <div class="energy-label" id="tb-ecard-shading-lbl"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </ha-card>
    `;
    this._cacheElements();
    this._scaffoldCreated = true;
  }

  _cacheElements() {
    const s = this.shadowRoot;
    if (!s) return;
    this._els = {
      haCard: s.querySelector('#tb-ha-card'),
      adviceContainer: s.querySelector('#tb-advice-container'),
      hdrTitle: s.querySelector('#tb-header-title'),
      hdrSub: s.querySelector('#tb-header-sub'),
      hdrBadge: s.querySelector('#tb-header-badge'),

      gaugeHeatSvg: s.querySelector('#tb-gauge-heat-svg'),
      gaugeHeatPath: s.querySelector('#tb-gauge-heat-path'),
      gaugeHeatVal: s.querySelector('#tb-gauge-heat-val'),
      gaugeHeatStop1: s.querySelector('#tb-grad-heat-stop1'),
      gaugeHeatStop2: s.querySelector('#tb-grad-heat-stop2'),
      gaugeHeatIcon: s.querySelector('#tb-gauge-heat-icon'),
      gaugeHeatLabel: s.querySelector('#tb-gauge-heat-label-text'),

      gaugeAcSvg: s.querySelector('#tb-gauge-ac-svg'),
      gaugeAcPath: s.querySelector('#tb-gauge-ac-path'),
      gaugeAcVal: s.querySelector('#tb-gauge-ac-val'),
      gaugeAcStop1: s.querySelector('#tb-grad-ac-stop1'),
      gaugeAcStop2: s.querySelector('#tb-grad-ac-stop2'),
      gaugeAcIcon: s.querySelector('#tb-gauge-ac-icon'),
      gaugeAcLabel: s.querySelector('#tb-gauge-ac-label-text'),

      metricNetBlock: s.querySelector('#tb-metric-net-block'),
      metricNetVal: s.querySelector('#tb-metric-net-val'),
      metricNetLbl: s.querySelector('#tb-metric-net-lbl'),
      metricVentBlock: s.querySelector('#tb-metric-vent-block'),
      metricVentIcon: s.querySelector('#tb-metric-vent-icon'),
      metricVentVal: s.querySelector('#tb-metric-vent-val'),
      metricVentLbl: s.querySelector('#tb-metric-vent-lbl'),
      metricTimeBlock: s.querySelector('#tb-metric-time-block'),
      metricTimeIcon: s.querySelector('#tb-metric-time-icon'),
      metricTimeVal: s.querySelector('#tb-metric-time-val'),
      metricTimeLbl: s.querySelector('#tb-metric-time-lbl'),
      metricCondBlock: s.querySelector('#tb-metric-cond-block'),
      metricCondVal: s.querySelector('#tb-metric-cond-val'),
      metricCondLbl: s.querySelector('#tb-metric-cond-lbl'),

      secVentTitle: s.querySelector('#tb-sec-vent-title'),
      vrowWinDot: s.querySelector('#tb-vrow-win-dot'),
      vrowWinLbl: s.querySelector('#tb-vrow-win-lbl'),
      vrowWinVal: s.querySelector('#tb-vrow-win-val'),
      vrowVentDot: s.querySelector('#tb-vrow-vent-dot'),
      vrowVentLbl: s.querySelector('#tb-vrow-vent-lbl'),
      vrowVentVal: s.querySelector('#tb-vrow-vent-val'),
      vrowWindRow: s.querySelector('#tb-vrow-wind-row'),
      vrowWindLbl: s.querySelector('#tb-vrow-wind-lbl'),
      vrowWindVal: s.querySelector('#tb-vrow-wind-val'),
      vrowAchRow: s.querySelector('#tb-vrow-ach-row'),
      vrowAchLbl: s.querySelector('#tb-vrow-ach-lbl'),
      vrowAchVal: s.querySelector('#tb-vrow-ach-val'),
      vrowCurtainsRow: s.querySelector('#tb-vrow-curtains-row'),
      vrowCurtainsDot: s.querySelector('#tb-vrow-curtains-dot'),
      vrowCurtainsLbl: s.querySelector('#tb-vrow-curtains-lbl'),
      vrowCurtainsVal: s.querySelector('#tb-vrow-curtains-val'),
      vrowCurtainsNote: s.querySelector('#tb-vrow-curtains-note'),
      vrowSolarLbl: s.querySelector('#tb-vrow-solar-lbl'),
      vrowSolarVal: s.querySelector('#tb-vrow-solar-val'),
      vrowWallLbl: s.querySelector('#tb-vrow-wall-lbl'),
      vrowWallVal: s.querySelector('#tb-vrow-wall-val'),
      vrowKLbl: s.querySelector('#tb-vrow-k-lbl'),
      vrowKVal: s.querySelector('#tb-vrow-k-val'),
      vrowInsulLbl: s.querySelector('#tb-vrow-insul-lbl'),
      vrowInsulVal: s.querySelector('#tb-vrow-insul-val'),
      vrowWinKNote: s.querySelector('#tb-vrow-win-k-note'),

      secAcIcon: s.querySelector('#tb-sec-ac-icon'),
      secAcTitle: s.querySelector('#tb-sec-ac-title'),
      secAcGrid: s.querySelector('#tb-sec-ac-grid'),

      trendTitle: s.querySelector('#tb-trend-title'),
      trendHeatLbl: s.querySelector('#tb-trend-heat-lbl'),
      trendHvacDot: s.querySelector('#tb-trend-hvac-dot'),
      trendHvacLbl: s.querySelector('#tb-trend-hvac-lbl'),

      secEnergyTitle: s.querySelector('#tb-sec-energy-title'),
      ecardDailyIcon: s.querySelector('#tb-ecard-daily-icon'),
      ecardDailyVal: s.querySelector('#tb-ecard-daily-val'),
      ecardDailyLbl: s.querySelector('#tb-ecard-daily-lbl'),
      ecardTotalVal: s.querySelector('#tb-ecard-total-val'),
      ecardTotalLbl: s.querySelector('#tb-ecard-total-lbl'),
      ecardHeatVal: s.querySelector('#tb-ecard-heat-val'),
      ecardHeatLbl: s.querySelector('#tb-ecard-heat-lbl'),
      ecardAcIcon: s.querySelector('#tb-ecard-ac-icon'),
      ecardAcVal: s.querySelector('#tb-ecard-ac-val'),
      ecardAcLbl: s.querySelector('#tb-ecard-ac-lbl'),
      ecardCostVal: s.querySelector('#tb-ecard-cost-val'),
      ecardCostUnit: s.querySelector('#tb-ecard-cost-unit'),
      ecardCostLbl: s.querySelector('#tb-ecard-cost-lbl'),
      ecardShadingVal: s.querySelector('#tb-ecard-shading-val'),
      ecardShadingUnit: s.querySelector('#tb-ecard-shading-unit'),
      ecardShadingLbl: s.querySelector('#tb-ecard-shading-lbl'),
    };
  }

  _render() {
    try {
      const prefix = this._derivePrefix();
      if (!this._autoDiscovered || this._autoDiscoveredPrefix !== prefix) {
        this._autoDiscovered = autoDiscoverEntities(this._hass, prefix);
        this._autoDiscoveredPrefix = prefix;
      }

      if (!this._hass || !this._hass.states || (!this._resolveEntity('heat_gain') && !this._resolveEntity('net_balance') && !this._config.heat_gain)) {
        this._renderPreview();
        return;
      }

      const keys = Object.keys(SENSOR_MAP);
      const parts = keys.map(k => {
        const eid = this._resolveEntity(k);
        if (!eid) return '';
        const s = this._hass.states[eid];
        if (!s) return '';
        return `${eid}=${s.state}|${JSON.stringify(s.attributes)}`;
      });
      const hash = parts.join(';;') + `;compact=${Boolean(this._config.compact || this._config.compact_view)};hver=${this._historyVersion || 0}`;
      if (hash === this._lastHash && this._scaffoldCreated) return;
      this._lastHash = hash;

      if (!this._scaffoldCreated || !this._els || !this._els.haCard) {
        this._createScaffold();
      }

      const isCompact = Boolean(this._config.compact || this._config.compact_view);
      const cardTitle = this._config.title ? escapeHtml(this._config.title) : this._t('title');

      // Read values
      const heatGain = this._getState('heat_gain');
      const acCooling = this._getState('ac_cooling');
      const netBalance = this._getState('net_balance');
      const cop = this._getState('ac_cop');
      const time1c = this._getState('time_to_1c');
      const dailyBal = this._getState('daily_balance');
      const totalBal = this._getState('total_balance');
      const heatAbsorbed = this._getState('heat_absorbed');
      const acEnergy = this._getState('ac_energy');
      const condensation = this._getState('condensation_rate');

      // AC cooling & heating attributes
      const isHeating = Boolean(this._getAttr('ac_cooling', 'is_heating') || this._getAttr('net_balance', 'is_heating'));
      const deltaT = this._getAttr('ac_cooling', 'delta_t_ac_c');
      const exitTemp = this._getAttr('ac_cooling', 'ac_exit_temperature_c');
      const calcExitTemp = this._getAttr('ac_cooling', 'ac_calc_exit_temperature_c');
      const hasMeasured = this._getAttr('ac_cooling', 'has_measured_exit_sensor');
      const sensible = this._getAttr('ac_cooling', 'sensible_cooling_w');
      const latent = this._getAttr('ac_cooling', 'latent_cooling_w');
      const shr = this._getAttr('ac_cooling', 'shr_percent');
      const enthalpy = this._getAttr('ac_cooling', 'air_enthalpy_in_kj_kg');
      const airflow = this._getAttr('ac_cooling', 'ac_airflow_m3h');
      const dewIn = this._getAttr('ac_cooling', 'indoor_dew_point_c');
      const dewOut = this._getAttr('ac_cooling', 'outdoor_dew_point_c');

      // Ventilation & Thermal sources attributes
      const pVent = this._getAttr('heat_gain', 'p_vent_w') ?? this._getAttr('net_balance', 'p_vent_w');
      const pSolar = this._getAttr('heat_gain', 'p_solar_w');
      const pWall = this._getAttr('heat_gain', 'p_wall_w');
      const windowOpen = this._getAttr('heat_gain', 'window_is_open') ?? this._getAttr('net_balance', 'window_is_open');
      const windSpeed = this._getAttr('heat_gain', 'wind_speed_ms');
      const windDir = this._getAttr('heat_gain', 'wind_dir_deg');
      const windACH = this._getAttr('heat_gain', 'ventilation_ach');

      // Empirical K-Factor attributes
      const empiricalK = this._getState('empirical_k_factor') ?? this._getAttr('heat_gain', 'hlc_w_k');
      const empiricalKDev = this._getAttr('empirical_k_factor', 'deviation_percent');
      const empiricalKGrade = this._getAttr('empirical_k_factor', 'insulation_grade');

      // Cost, Savings & Recommendation states
      const acCost = this._getState('ac_cost');
      const dailySavings = this._getState('daily_savings');
      const boolRecOpen = this._getBoolState('rec_open_window');
      const recOpenWin = boolRecOpen !== null ? boolRecOpen : Boolean(this._getAttr('heat_gain', 'recommend_open_window'));
      const boolRecClose = this._getBoolState('rec_close_curtains');
      const recCloseCur = boolRecClose !== null ? boolRecClose : Boolean(this._getAttr('heat_gain', 'recommend_close_curtains'));
      const currencySymbol = escapeHtml(this._getAttr('ac_cost', 'unit_of_measurement') || '₴');

      // Curtains & Shading attributes
      const curtainsClosed = this._getAttr('heat_gain', 'curtains_closed');
      const curtainsState = this._getAttr('heat_gain', 'curtains_state');
      const illuminanceLux = this._getAttr('heat_gain', 'illuminance_lux');
      const curtainsNote = this._getAttr('heat_gain', 'curtains_note');
      const curtainReducePct = this._getAttr('heat_gain', 'curtain_glass_reduce_percent') || 74;

      // time_to_1c attributes
      const direction = this._getAttr('time_to_1c', 'direction') || 'equilibrium';
      const dirInfo = this._dirIcon(direction);

      // Colors & formatting
      const balColor = this._balanceColor(netBalance);
      const balBg = this._balanceBg(netBalance);
      const dailyColor = this._balanceColor(dailyBal);
      const timeDisplay = this._fmtTime(time1c, direction);

      const ventColor = windowOpen ? (pVent > 20 ? '#FF7A3C' : (pVent < -20 ? '#4DA3FF' : '#00C896')) : '#9CA3AF';
      const ventValText = !windowOpen ? `${this._t('window_closed')} (0 W)` : (pVent !== null && pVent !== undefined ? (pVent > 0 ? '+' : '') + this._fmt(pVent, 0) + ' W' : '—');

      const modeBadge = isHeating ? `🔥 ${this._t('heat_mode')}` : `❄️ ${this._t('cool_mode')}`;
      const copText = cop !== null ? `COP ${this._fmt(cop, 2)}` : '';
      const shrText = (!isHeating && shr !== null) ? `SHR ${this._fmt(shr, 0)}%` : '';
      const ventHeaderBadge = windowOpen ? (pVent !== null ? (pVent >= 0 ? `🪟 +${Math.round(pVent)}W` : `🪟 ${Math.round(pVent)}W`) : `🪟 ${this._t('window_open')}`) : `🪟 ${this._t('window_closed')}`;
      const subtitle = [modeBadge, copText, shrText, ventHeaderBadge].filter(Boolean).join(' · ');

      const acGaugeTitle = isHeating ? this._t('ac_heating') : this._t('ac_cooling');
      const acGaugeColor = isHeating ? '#FF7A3C' : '#4DA3FF';
      const acGaugeSubColor = isHeating ? '#FFB199' : '#93C5FD';
      const acGaugeIcon = isHeating ? this._icons.fire : this._icons.snowflake;
      const acSectionTitle = isHeating ? this._t('heating_perf') : this._t('ac_cooling_perf');
      const acSectionIcon = isHeating ? this._icons.fireLg : this._icons.snowflakeLg;

      const acRows = [
        { label: this._t('ac_dt'), value: deltaT, unit: '°C', dec: 1, color: '#374151' },
        { label: hasMeasured ? this._t('exit_temp_meas') : this._t('exit_temp'), value: exitTemp, unit: '°C', dec: 1, color: hasMeasured ? (isHeating ? '#FF7A3C' : '#4DA3FF') : '#374151' },
        ...(hasMeasured ? [{ label: this._t('exit_temp_calc'), value: calcExitTemp, unit: '°C', dec: 1, color: '#FACC15' }] : []),
        { label: isHeating ? this._t('sensible_heat_heating') : this._t('sensible_heat'), value: sensible, unit: 'W', dec: 0, color: '#374151' },
        ...(!isHeating ? [{ label: this._t('latent_heat'), value: latent, unit: 'W', dec: 0, color: '#374151' }] : []),
        ...(!isHeating ? [{ label: this._t('shr'), value: shr, unit: '%', dec: 1, color: '#374151' }] : []),
        { label: this._t('enthalpy'), value: enthalpy, unit: 'kJ/kg', dec: 1, color: '#374151' },
        { label: this._t('airflow'), value: airflow, unit: 'm³/h', dec: 0, color: '#00C896' },
        { label: this._t('dew_point_in'), value: dewIn, unit: '°C', dec: 1, color: '#4DA3FF' },
        { label: this._t('dew_point_out'), value: dewOut, unit: '°C', dec: 1, color: '#4DA3FF' },
      ];

      // Fetch history asynchronously
      this._fetchHistory();

      const acRowsHtml = acRows.map(r => `
        <div class="ac-row">
          <span class="ac-dot" style="background:${r.color}"></span>
          <span class="ac-label">${escapeHtml(r.label)}</span>
          <span class="ac-val">${r.value !== null && r.value !== undefined ? this._fmt(r.value, r.dec) : '—'} <span class="ac-unit">${r.value !== null && r.value !== undefined ? escapeHtml(r.unit) : ''}</span></span>
        </div>`).join('');

      // Targeted DOM updates (no innerHTML wipe!)
      const els = this._els;
      els.haCard.className = `${isHeating ? 'heating-theme' : 'cooling-theme'} ${isCompact ? 'compact-mode' : ''}`;

      // Banners (accessible & sanitized)
      let adviceHtml = '';
      if (recOpenWin) {
        adviceHtml += `<div class="advice-banner advice-window"><span>🍃 <b>${escapeHtml(this._t('open_win_rec'))}</b></span></div>`;
      }
      if (recCloseCur) {
        adviceHtml += `<div class="advice-banner advice-curtains"><span>☀️ <b>${escapeHtml(this._t('close_cur_rec'))}</b></span></div>`;
      }
      els.adviceContainer.innerHTML = adviceHtml;

      // Header
      els.hdrTitle.textContent = cardTitle;
      els.hdrSub.textContent = subtitle;
      els.hdrSub.style.display = subtitle ? 'block' : 'none';
      els.hdrBadge.textContent = `${netBalance !== null ? (netBalance > 0 ? '+' : '') + this._fmt(netBalance, 0) : '—'} W`;

      // Heat Gauge
      const heatIsLoss = heatGain !== null && heatGain < 0;
      const heatColor1 = heatIsLoss ? '#4DA3FF' : '#FF7A3C';
      const heatColor2 = heatIsLoss ? '#93C5FD' : '#FFB199';
      const heatLabel = heatIsLoss ? this._t('heat_loss') : this._t('heat_gain');
      const heatIconSvg = heatIsLoss ? this._icons.snowflake : this._icons.sun;
      const circ = 172.7876;
      const pctHeat = Math.min(1, Math.max(0, Math.abs(heatGain || 0) / 3500));
      const offsetHeat = circ * (1 - pctHeat);

      els.gaugeHeatStop1.setAttribute('stop-color', heatColor1);
      els.gaugeHeatStop2.setAttribute('stop-color', heatColor2);
      els.gaugeHeatPath.setAttribute('stroke-dashoffset', offsetHeat.toFixed(1));
      els.gaugeHeatVal.textContent = heatGain !== null ? this._fmt(heatGain, 0) : '—';
      els.gaugeHeatIcon.innerHTML = heatIconSvg;
      els.gaugeHeatLabel.textContent = heatLabel;
      if (els.gaugeHeatSvg) {
        els.gaugeHeatSvg.setAttribute('aria-label', `${heatLabel}: ${heatGain !== null ? this._fmt(heatGain, 0) : '—'} W`);
      }

      // AC Gauge
      const pctAc = Math.min(1, Math.max(0, Math.abs(acCooling || 0) / 3500));
      const offsetAc = circ * (1 - pctAc);

      els.gaugeAcStop1.setAttribute('stop-color', acGaugeColor);
      els.gaugeAcStop2.setAttribute('stop-color', acGaugeSubColor);
      els.gaugeAcPath.setAttribute('stroke-dashoffset', offsetAc.toFixed(1));
      els.gaugeAcVal.textContent = acCooling !== null ? this._fmt(acCooling, 0) : '—';
      els.gaugeAcIcon.innerHTML = acGaugeIcon;
      els.gaugeAcLabel.textContent = acGaugeTitle;
      if (els.gaugeAcSvg) {
        els.gaugeAcSvg.setAttribute('aria-label', `${acGaugeTitle}: ${acCooling !== null ? this._fmt(acCooling, 0) : '—'} W`);
      }

      // Metrics Bar
      els.metricNetVal.innerHTML = `${netBalance !== null ? (netBalance > 0 ? '+' : '') + this._fmt(netBalance, 0) : '—'} <span class="metric-unit">W</span>`;
      els.metricNetLbl.textContent = this._t('net_balance');
      if (els.metricNetBlock) {
        els.metricNetBlock.setAttribute('aria-label', `${this._t('net_balance')}: ${netBalance !== null ? (netBalance > 0 ? '+' : '') + this._fmt(netBalance, 0) : '—'} W`);
      }

      els.metricVentVal.innerHTML = `${pVent !== null && pVent !== undefined && windowOpen ? (pVent > 0 ? '+' : '') + this._fmt(pVent, 0) : (windowOpen ? '0' : 'Off')} <span class="metric-unit">${windowOpen ? 'W' : ''}</span>`;
      els.metricVentVal.style.color = ventColor;
      els.metricVentLbl.textContent = this._t('ventilation');
      if (els.metricVentBlock) {
        els.metricVentBlock.setAttribute('aria-label', `${this._t('ventilation')}: ${windowOpen ? this._t('window_open') : this._t('window_closed')}, ${ventValText}`);
      }

      els.metricTimeIcon.textContent = dirInfo.sym;
      els.metricTimeVal.textContent = timeDisplay;
      els.metricTimeLbl.textContent = this._t('to_1c');
      if (els.metricTimeBlock) {
        els.metricTimeBlock.setAttribute('aria-label', `${this._t('to_1c')}: ${timeDisplay}`);
      }

      els.metricCondVal.innerHTML = `${condensation !== null ? this._fmt(condensation, 2) : '—'} <span class="metric-unit">L/h</span>`;
      els.metricCondLbl.textContent = this._t('condensation');
      if (els.metricCondBlock) {
        els.metricCondBlock.setAttribute('aria-label', `${this._t('condensation')}: ${condensation !== null ? this._fmt(condensation, 2) : '—'} L/h`);
      }

      // Ventilation & Sources Section
      els.secVentTitle.textContent = this._t('vent_heat_exchange');
      els.vrowWinDot.style.background = windowOpen ? '#FF7A3C' : '#9CA3AF';
      els.vrowWinLbl.textContent = this._t('window');
      els.vrowWinVal.textContent = windowOpen ? this._t('window_open') : this._t('window_closed');
      els.vrowWinVal.style.color = windowOpen ? '#FF7A3C' : '#00C896';

      els.vrowVentDot.style.background = ventColor;
      els.vrowVentLbl.textContent = this._t('ventilation');
      els.vrowVentVal.textContent = ventValText;
      els.vrowVentVal.style.color = ventColor;

      if (windSpeed !== null && windSpeed !== undefined) {
        els.vrowWindRow.style.display = 'flex';
        els.vrowWindLbl.textContent = this._t('wind');
        els.vrowWindVal.innerHTML = `${this._fmt(windSpeed, 1)} ${this._t('ms_unit')} <span class="ac-unit">(${this._fmt(windDir, 0)}°)</span>`;
      } else {
        els.vrowWindRow.style.display = 'none';
      }

      if (windACH !== null && windACH !== undefined && windowOpen) {
        els.vrowAchRow.style.display = 'flex';
        els.vrowAchLbl.textContent = this._t('air_change');
        els.vrowAchVal.innerHTML = `${this._fmt(windACH, 1)} <span class="ac-unit">${this._t('per_hour')}</span>`;
      } else {
        els.vrowAchRow.style.display = 'none';
      }

      if (curtainsState !== null && curtainsState !== undefined) {
        els.vrowCurtainsRow.style.display = 'flex';
        els.vrowCurtainsDot.style.background = curtainsClosed ? '#8B5CF6' : '#FF7A3C';
        els.vrowCurtainsLbl.textContent = this._t('curtains');
        els.vrowCurtainsVal.style.color = curtainsClosed ? '#8B5CF6' : '#FF7A3C';
        els.vrowCurtainsVal.innerHTML = `${curtainsClosed ? `${this._t('curtains_closed')} (-${curtainReducePct}%)` : this._t('curtains_open')} ${illuminanceLux !== null && illuminanceLux !== undefined ? '<span class="ac-unit">(' + Math.round(illuminanceLux) + ' lx)</span>' : ''}`;
        if (curtainsNote) {
          els.vrowCurtainsNote.style.display = 'block';
          els.vrowCurtainsNote.textContent = `🌙 ${this._translateCurtainsNote(curtainsNote)}`;
        } else {
          els.vrowCurtainsNote.style.display = 'none';
        }
      } else {
        els.vrowCurtainsRow.style.display = 'none';
        els.vrowCurtainsNote.style.display = 'none';
      }

      els.vrowSolarLbl.textContent = this._t('solar');
      els.vrowSolarVal.textContent = pSolar !== null && pSolar !== undefined ? '+' + this._fmt(pSolar, 0) + ' W' : '—';

      els.vrowWallLbl.textContent = this._t('walls');
      els.vrowWallVal.textContent = pWall !== null && pWall !== undefined ? (pWall > 0 ? '+' : '') + this._fmt(pWall, 0) + ' W' : '—';

      els.vrowKLbl.textContent = this._t('k_factor_actual');
      els.vrowKVal.innerHTML = empiricalK !== null ? `${this._fmt(empiricalK, 1)} W/K <span class="ac-unit">${empiricalKDev !== null ? '(' + (empiricalKDev > 0 ? '+' : '') + this._fmt(empiricalKDev, 0) + '%)' : ''}</span>` : '—';

      els.vrowInsulLbl.textContent = this._t('insulation');
      els.vrowInsulVal.textContent = this._translateGrade(empiricalKGrade);

      els.vrowWinKNote.style.display = windowOpen ? 'block' : 'none';
      els.vrowWinKNote.textContent = windowOpen ? `🪟 ${this._t('window_open_k_note')}` : '';

      // AC perf
      els.secAcIcon.innerHTML = acSectionIcon;
      els.secAcTitle.textContent = acSectionTitle;
      els.secAcGrid.innerHTML = acRowsHtml;

      // 24h Trend
      if (els.trendTitle) els.trendTitle.textContent = this._t('trend_24h');
      if (els.trendHeatLbl) els.trendHeatLbl.textContent = this._t('heat');
      if (els.trendHvacDot) els.trendHvacDot.style.background = acGaugeColor;
      if (els.trendHvacLbl) els.trendHvacLbl.textContent = isHeating ? this._t('heating') : this._t('cooling');

      // Energy
      els.secEnergyTitle.textContent = this._t('energy_cost_intel');
      els.ecardDailyIcon.style.color = dailyColor;
      els.ecardDailyVal.textContent = dailyBal !== null ? this._fmt(dailyBal, 1) : '—';
      els.ecardDailyVal.style.color = dailyColor;
      els.ecardDailyLbl.textContent = this._t('daily_balance');

      els.ecardTotalVal.textContent = totalBal !== null ? this._fmt(totalBal, 1) : '—';
      els.ecardTotalLbl.textContent = this._t('total_balance');

      els.ecardHeatVal.textContent = heatAbsorbed !== null ? this._fmt(heatAbsorbed, 1) : '—';
      els.ecardHeatLbl.textContent = this._t('heat_absorbed');

      els.ecardAcIcon.textContent = isHeating ? '🔥' : '❄';
      els.ecardAcIcon.style.color = acGaugeColor;
      els.ecardAcVal.textContent = acEnergy !== null ? this._fmt(acEnergy, 1) : '—';
      els.ecardAcVal.style.color = acGaugeColor;
      els.ecardAcLbl.textContent = this._t('ac_energy');

      els.ecardCostVal.textContent = acCost !== null ? this._fmt(acCost, 2) : '—';
      els.ecardCostUnit.textContent = currencySymbol;
      els.ecardCostLbl.textContent = this._t('ac_cost');

      els.ecardShadingVal.textContent = dailySavings !== null ? this._fmt(dailySavings, 2) : '—';
      els.ecardShadingUnit.textContent = `${currencySymbol}${this._t('per_day')}`;
      els.ecardShadingLbl.textContent = this._t('shading_savings');

      // ECharts Update without canvas destruction
      this._initEChart(isHeating);
      this._setupResizeObserver();
    } catch (err) {
      console.error('ThermalBalanceCard render error:', err);
    }
  }

  _renderPreview() {
    const isRu = (this._hass && (this._hass.locale?.language || this._hass.language) || '').toLowerCase().startsWith('ru');
    const winClosedText = isRu ? 'Закрыто' : 'Closed';
    this.shadowRoot.innerHTML = `
      <style>${this._css()}</style>
      <ha-card class="cooling-theme">
        <div class="tb-card">
          <div class="header">
            <div class="header-left">
              <div class="header-icon">${this._icons.thermo}</div>
              <div class="header-text">
                <div class="header-title">${this._t('title')}</div>
                <div class="header-sub">COP 3.33 · SHR 85% · 🪟 ${winClosedText}</div>
              </div>
            </div>
            <div class="header-badge" style="background:var(--tb-theme-badge-bg); color:var(--tb-theme-accent); border:1px solid var(--tb-theme-border)">
              -504 W
            </div>
          </div>
          <div class="gauges-row">
            ${this._gauge(927, 3500, '#FF7A3C', '#FFB199', this._t('heat_gain'), this._icons.sun)}
            ${this._gauge(1431, 3500, '#4DA3FF', '#93C5FD', this._t('ac_cooling'), this._icons.snowflake)}
          </div>
        </div>
      </ha-card>`;
  }

  /* ─── Styles ─── */

  _css() {
    return `
      :host {
        --tb-card-bg: var(--ha-card-background, var(--card-background-color, #0B1220));
        --tb-section-bg: var(--ha-card-background-subcard, var(--primary-background-color, #162032));
        --tb-energy-bg: var(--ha-card-background, var(--card-background-color, #0B1220));
        --tb-primary: var(--primary-text-color, #FFFFFF);
        --tb-secondary: var(--secondary-text-color, #9CA3AF);
        --tb-text-contrast: #D1D5DB;
        --tb-border: var(--divider-color, #233045);
        --tb-border-hover: rgba(255, 255, 255, 0.2);
        --tb-heat: #FF7A3C;
        --tb-cool: #4DA3FF;
        --tb-cop: #8B5CF6;
        --tb-pos: #FF7A3C;
        --tb-neg: #4DA3FF;
        --tb-eq: #00C896;
        --tb-warn: #FACC15;
        font-family: var(--paper-font-body1_-_font-family, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
        display: block;
        width: 100%;
        box-sizing: border-box;
      }
      ha-card {
        background: var(--tb-card-bg);
        border-radius: var(--ha-card-border-radius, 18px);
        box-shadow: var(--ha-card-box-shadow, 0 10px 36px rgba(0,0,0,0.55)), 0 0 25px var(--tb-theme-glow);
        border: 1px solid var(--tb-theme-border);
        overflow: hidden;
        color: var(--tb-primary);
        padding: 0;
        transition: border-color 0.4s ease, box-shadow 0.4s ease;
      }
      ha-card.cooling-theme {
        --tb-theme-accent: #4DA3FF;
        --tb-theme-glow: rgba(77, 163, 255, 0.22);
        --tb-theme-border: rgba(77, 163, 255, 0.25);
        --tb-theme-badge-bg: rgba(77, 163, 255, 0.15);
      }
      ha-card.heating-theme {
        --tb-theme-accent: #FF7A3C;
        --tb-theme-glow: rgba(255, 122, 60, 0.25);
        --tb-theme-border: rgba(255, 122, 60, 0.35);
        --tb-theme-badge-bg: rgba(255, 122, 60, 0.18);
      }
      .tb-card {
        padding: 16px;
        container-type: inline-size;
        container-name: tb-card;
      }
      .advice-banner {
        padding: 10px 14px;
        border-radius: 12px;
        font-size: 13.5px;
        line-height: 1.4;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
        font-weight: 600;
      }
      .advice-window {
        background: rgba(0, 200, 150, 0.15);
        border: 1px solid rgba(0, 200, 150, 0.4);
        color: #00E6AB;
      }
      .advice-curtains {
        background: rgba(255, 122, 60, 0.15);
        border: 1px solid rgba(255, 122, 60, 0.4);
        color: #FF8F56;
      }
      .card-layout {
        display: grid;
        grid-template-columns: 1fr;
        gap: 12px;
        align-items: stretch;
      }
      @container tb-card (min-width: 580px) {
        .card-layout {
          grid-template-columns: repeat(2, minmax(0, 1fr));
          align-items: stretch;
        }
      }
      .card-col {
        display: flex;
        flex-direction: column;
        gap: 12px;
        min-width: 0;
        height: 100%;
      }
      .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
      }
      .header-left {
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .header-icon {
        width: 36px; height: 36px;
        display: flex; align-items: center; justify-content: center;
        background: var(--tb-theme-badge-bg);
        color: var(--tb-theme-accent);
        border-radius: 10px;
      }
      .header-icon svg { width: 20px; height: 20px; }
      .header-title {
        font-size: 17px;
        font-weight: 800;
        letter-spacing: 0.3px;
        color: var(--tb-primary);
      }
      .header-sub {
        font-size: 12px;
        color: var(--tb-secondary);
        margin-top: 1px;
        letter-spacing: 0.2px;
        font-weight: 500;
      }
      .header-badge {
        font-size: 14px;
        font-weight: 800;
        padding: 5px 12px;
        border-radius: 20px;
        white-space: nowrap;
        transition: color 0.3s ease, background 0.3s ease, border-color 0.3s ease;
      }
      .gauges-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
      }
      .gauge-card {
        background: var(--tb-section-bg);
        border-radius: 12px;
        border: 1px solid var(--tb-border);
        padding: 10px 8px 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        transition: border-color 0.3s ease;
      }
      .gauge-card:hover {
        border-color: var(--tb-border-hover);
      }
      .gauge-svg {
        width: 100%;
        max-width: 200px;
      }
      .gauge-label {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13.5px;
        font-weight: 600;
        color: var(--tb-text-contrast);
        margin-top: 6px;
      }
      .gauge-icon { display: flex; align-items: center; }
      .metrics-bar {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
      }
      .metric-block {
        background: var(--tb-section-bg);
        border: 1px solid var(--tb-border);
        border-radius: 10px;
        padding: 10px 6px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3px;
        transition: border-color 0.3s ease;
      }
      .metric-block:hover {
        border-color: var(--tb-border-hover);
      }
      .metric-icon { font-size: 15px; line-height: 1; }
      .metric-val {
        font-size: 15px;
        font-weight: 800;
        transition: color 0.3s ease;
        white-space: nowrap;
      }
      .metric-unit { font-size: 11px; opacity: 0.85; font-weight: 500; }
      .metric-label {
        font-size: 11px;
        font-weight: 500;
        color: var(--tb-text-contrast);
        letter-spacing: 0.1px;
      }
      .section {
        background: var(--tb-section-bg);
        border: 1px solid var(--tb-border);
        border-radius: 12px;
        padding: 12px 14px;
        transition: border-color 0.3s ease;
      }
      .section:hover {
        border-color: var(--tb-border-hover);
      }
      .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13.5px;
        font-weight: 700;
        color: var(--tb-primary);
        margin-bottom: 10px;
        letter-spacing: 0.2px;
      }
      .section-title svg { flex-shrink: 0; }
      .ac-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0;
      }
      @container tb-card (min-width: 500px) {
        .ac-grid {
          grid-template-columns: 1fr 1fr;
        }
      }
      .ac-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        padding: 7px 6px;
        border-bottom: 1px solid var(--tb-border);
        font-size: 12.5px;
        min-width: 0;
      }
      .ac-row:last-child { border-bottom: none; }
      @container tb-card (min-width: 500px) {
        .ac-row:nth-last-child(-n+2) { border-bottom: none; }
      }
      .ac-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
      }
      .ac-label {
        color: var(--tb-text-contrast);
        font-weight: 500;
        flex: 1;
        min-width: 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .ac-val {
        font-weight: 700;
        color: var(--tb-primary);
        white-space: nowrap;
        flex-shrink: 0;
        text-align: right;
      }
      .ac-unit {
        font-weight: 400;
        font-size: 10.5px;
        opacity: 0.85;
      }
      .curtains-note {
        grid-column: 1 / -1;
        font-size: 12.5px;
        color: var(--tb-text-contrast);
        padding: 3px 6px 6px 20px;
        line-height: 1.4;
        text-align: left;
      }
      .energy-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
      }
      .energy-card {
        background: var(--tb-energy-bg);
        border: 1px solid var(--tb-border);
        border-radius: 10px;
        padding: 10px 10px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        transition: border-color 0.3s ease;
      }
      .energy-card:hover {
        border-color: var(--tb-border-hover);
      }
      .energy-icon { font-size: 18px; margin-bottom: 2px; }
      .energy-val {
        font-size: 17px;
        font-weight: 800;
        transition: color 0.3s ease;
        line-height: 1.2;
      }
      .energy-unit {
        font-size: 11px;
        color: var(--tb-secondary);
        font-weight: 500;
      }
      .energy-label {
        font-size: 11px;
        font-weight: 500;
        color: var(--tb-secondary);
        margin-top: 2px;
        letter-spacing: 0.2px;
      }
      .trend-legend {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 14px;
        font-size: 12px;
        font-weight: 600;
        color: var(--tb-secondary);
      }
      .legend-item {
        display: flex;
        align-items: center;
        gap: 5px;
      }
      .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
      }
      .trend-chart-container {
        width: 100%;
        margin-top: 6px;
      }
      .trend-svg {
        width: 100%;
        height: 60px;
        overflow: visible;
      }

      /* ─── Container Queries: Automatic Responsive Compact Layout (<= 480px) ─── */
      @container tb-card (max-width: 480px) {
        .tb-card {
          padding: 12px;
        }
        .card-layout {
          grid-template-columns: 1fr !important;
          gap: 10px;
        }
        .gauges-row {
          gap: 8px;
        }
        .gauge-card {
          padding: 6px 4px 6px;
        }
        .gauge-svg {
          max-width: 130px;
        }
        .gauge-label {
          font-size: 12px;
          margin-top: 2px;
        }
        .metrics-bar {
          grid-template-columns: repeat(2, 1fr) !important;
          gap: 6px;
        }
        .metric-block {
          padding: 6px 4px;
        }
        .energy-grid {
          grid-template-columns: repeat(3, 1fr) !important;
          gap: 6px;
        }
        .energy-card {
          padding: 6px 4px;
        }
        .energy-val {
          font-size: 15px;
        }
        #echart-container {
          min-height: 120px !important;
        }
      }

      @container tb-card (max-width: 330px) {
        .energy-grid {
          grid-template-columns: repeat(2, 1fr) !important;
        }
      }

      /* ─── Compact Mode (Config Override) ─── */
      ha-card.compact-mode .tb-card {
        padding: 12px;
      }
      ha-card.compact-mode .card-layout {
        grid-template-columns: 1fr !important;
        gap: 10px;
      }
      ha-card.compact-mode .gauges-row {
        gap: 8px;
      }
      ha-card.compact-mode .gauge-card {
        padding: 6px 4px 6px;
      }
      ha-card.compact-mode .gauge-svg {
        max-width: 130px;
      }
      ha-card.compact-mode .gauge-label {
        font-size: 12px;
        margin-top: 2px;
      }
      ha-card.compact-mode .metrics-bar {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 6px;
      }
      ha-card.compact-mode .metric-block {
        padding: 6px 4px;
      }
      ha-card.compact-mode .energy-grid {
        grid-template-columns: repeat(3, 1fr) !important;
        gap: 6px;
      }
      ha-card.compact-mode .energy-card {
        padding: 6px 4px;
      }
      ha-card.compact-mode .energy-val {
        font-size: 15px;
      }
      ha-card.compact-mode #echart-container {
        min-height: 110px !important;
      }

      @media (max-width: 360px) {
        .metrics-bar { grid-template-columns: repeat(2, 1fr); }
        .metric-val { font-size: 14px; }
      }
    `;
  }
}

/* ─── Register Custom Elements ─── */
if (!customElements.get('thermal-balance-card')) {
  customElements.define('thermal-balance-card', ThermalBalanceCard);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'thermal-balance-card',
  name: 'Thermal Balance',
  description: 'Thermal balance monitoring card with live metrics and energy tracking.',
  icon: 'mdi:home-thermometer',
  preview: true,
  documentationURL: 'https://github.com/meksspirt/thermal_balance',
});
