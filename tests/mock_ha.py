"""Lightweight Home Assistant mock harness for standalone unit testing."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from enum import StrEnum
from types import ModuleType
from typing import Any, Callable
from unittest.mock import MagicMock
try:
    import voluptuous as vol
except ImportError:
    class MockVol:
        class Schema:
            def __init__(self, schema: Any = None) -> None:
                self.schema = schema

            def __call__(self, data: Any) -> Any:
                return data

        class Required:
            def __init__(self, key: Any, default: Any = None, description: Any = None) -> None:
                self.key = key
                self.default = default

        class Optional:
            def __init__(self, key: Any, default: Any = None, description: Any = None) -> None:
                self.key = key
                self.default = default

        class Coerce:
            def __init__(self, type_fn: Any) -> None:
                self.type_fn = type_fn

            def __call__(self, v: Any) -> Any:
                return self.type_fn(v)

        class error:
            class SchemaError(Exception):
                pass

    vol = MockVol()
    sys.modules["voluptuous"] = vol


class MockState:
    """Mock Home Assistant State object."""

    def __init__(
        self,
        state: str,
        attributes: dict[str, Any] | None = None,
        last_updated: Any = None,
    ) -> None:
        self.state = state
        self.attributes = attributes or {}
        self.last_updated = last_updated or datetime.now(timezone.utc)


class MockStateMachine:
    """Mock Home Assistant state machine."""

    def __init__(self) -> None:
        self._states: dict[str, MockState] = {}

    def get(self, entity_id: str) -> MockState | None:
        return self._states.get(entity_id)

    def set(self, entity_id: str, state: str, attributes: dict[str, Any] | None = None) -> None:
        self._states[entity_id] = MockState(state, attributes)


class MockConfig:
    """Mock Home Assistant config."""

    def __init__(self, currency: str = "USD") -> None:
        self.currency = currency


class MockServiceRegistry:
    """Mock service registry to register and invoke services in tests."""

    def __init__(self) -> None:
        self.services: dict[str, dict[str, Callable]] = {}

    def async_register(
        self,
        domain: str,
        service: str,
        service_func: Callable,
        schema: Any = None,
        supports_response: Any = None,
    ) -> None:
        self.services.setdefault(domain, {})[service] = service_func

    async def async_call(
        self,
        domain: str,
        service: str,
        service_data: dict[str, Any] | None = None,
    ) -> Any:
        import inspect
        func = self.services.get(domain, {}).get(service)
        if func:
            call = MagicMock()
            call.data = service_data or {}
            if inspect.iscoroutinefunction(func):
                return await func(call)
            return func(call)
        return None


class MockConfigEntries:
    """Mock config entries container on HomeAssistant."""

    def __init__(self) -> None:
        self._entries: list[Any] = []

    def async_entries(self, domain: str | None = None) -> list[Any]:
        if domain:
            return [e for e in self._entries if getattr(e, "domain", "thermal_balance") == domain]
        return list(self._entries)

    def add(self, entry: Any) -> None:
        self._entries.append(entry)

    def async_update_entry(
        self,
        entry: Any,
        *,
        data: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> None:
        if data is not None:
            entry.data = data
        if options is not None:
            entry.options = options
        if hasattr(entry, "_update_listeners"):
            for listener in entry._update_listeners:
                listener(None, entry)


class MockHomeAssistant:
    """Mock Home Assistant instance."""

    def __init__(self) -> None:
        self.states = MockStateMachine()
        self.config = MockConfig()
        self.services = MockServiceRegistry()
        self.config_entries = MockConfigEntries()
        from unittest.mock import AsyncMock
        self.http = MagicMock()
        self.http.async_register_static_paths = AsyncMock()

    async def async_add_executor_job(self, target: Callable[..., Any], *args: Any) -> Any:
        return target(*args)


class MockConfigEntry:
    """Mock ConfigEntry object."""

    def __init__(
        self,
        entry_id: str = "test_entry_123",
        data: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
        title: str = "Thermal Balance",
        unique_id: str | None = None,
    ) -> None:
        self.entry_id = entry_id
        self.data = data or {}
        self.options = options or {}
        self.title = title
        self.unique_id = unique_id
        self.runtime_data: Any = None
        self._update_listeners: list[Callable] = []

    def add_update_listener(self, listener: Callable) -> Callable:
        self._update_listeners.append(listener)
        return lambda: self._update_listeners.remove(listener)


class Platform(StrEnum):
    """Mock Platform enum."""

    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    BUTTON = "button"
    NUMBER = "number"
    SELECT = "select"


def setup_mock_homeassistant() -> None:
    """Install mock homeassistant modules in sys.modules if not present."""
    if "homeassistant" in sys.modules and hasattr(sys.modules["homeassistant"], "_is_mock"):
        return

    ha = ModuleType("homeassistant")
    ha._is_mock = True
    ha.__path__ = []

    ha_const = ModuleType("homeassistant.const")
    ha_const.Platform = Platform
    ha_const.SUN_EVENT_SUNRISE = "sunrise"
    ha_const.SUN_EVENT_SUNSET = "sunset"

    class MockUnitOfEnergy(StrEnum):
        KILO_WATT_HOUR = "kWh"
        WATT_HOUR = "Wh"

    class MockUnitOfPower(StrEnum):
        WATT = "W"
        KILO_WATT = "kW"

    class MockUnitOfTemperature(StrEnum):
        CELSIUS = "°C"

    class MockUnitOfTime(StrEnum):
        MINUTES = "min"
        HOURS = "h"
        SECONDS = "s"

    class EntityCategory(StrEnum):
        CONFIG = "config"
        DIAGNOSTIC = "diagnostic"

    ha_const.UnitOfEnergy = MockUnitOfEnergy
    ha_const.UnitOfPower = MockUnitOfPower
    ha_const.UnitOfTemperature = MockUnitOfTemperature
    ha_const.UnitOfTime = MockUnitOfTime
    ha_const.EntityCategory = EntityCategory

    ha_core = ModuleType("homeassistant.core")
    ha_core.__path__ = []

    ha_config_entries = ModuleType("homeassistant.config_entries")
    ha_config_entries.__path__ = []

    ha_helpers = ModuleType("homeassistant.helpers")
    ha_helpers.__path__ = []

    ha_helpers_typing = ModuleType("homeassistant.helpers.typing")
    ha_helpers_typing.ConfigType = dict[str, Any]
    ha_helpers_typing.DiscoveryInfoType = dict[str, Any]

    ha_helpers_cv = ModuleType("homeassistant.helpers.config_validation")
    ha_helpers_cv.string = cv_string = lambda v: str(v)
    ha_helpers_cv.positive_float = lambda v: float(v)
    ha_helpers_cv.boolean = lambda v: bool(v)
    ha_helpers_cv.make_entity_service_schema = lambda schema: vol.Schema(schema)
    ha_helpers_cv.config_entry_only_config_schema = lambda domain: vol.Schema({})
    ha_helpers_cv.empty_config_schema = lambda domain: vol.Schema({})
    ha_helpers_cv.platform_only_config_schema = lambda domain: vol.Schema({})

    ha_helpers_event = ModuleType("homeassistant.helpers.event")
    ha_helpers_selector = ModuleType("homeassistant.helpers.selector")
    ha_helpers_entity = ModuleType("homeassistant.helpers.entity")
    ha_helpers_entity_platform = ModuleType("homeassistant.helpers.entity_platform")
    ha_helpers_entity_platform.AddEntitiesCallback = Callable
    ha_helpers_restore_state = ModuleType("homeassistant.helpers.restore_state")
    ha_helpers_update_coordinator = ModuleType("homeassistant.helpers.update_coordinator")

    class MockDeviceInfo:
        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)

    ha_helpers_entity.DeviceInfo = MockDeviceInfo
    ha_helpers_entity.EntityCategory = EntityCategory

    class MockRestoreEntity:
        async def async_get_last_state(self) -> Any:
            return getattr(self, "_mock_last_state", None)

    ha_helpers_restore_state.RestoreEntity = MockRestoreEntity

    class MockCoordinatorEntity:
        def __init__(self, coordinator: Any = None) -> None:
            self.coordinator = coordinator

        def __class_getitem__(cls, item: Any) -> Any:
            return cls

        @property
        def available(self) -> bool:
            if self.coordinator is not None:
                return getattr(self.coordinator, "last_update_success", True)
            return True

        @property
        def entity_category(self) -> Any:
            return getattr(self, "_attr_entity_category", None)

        async def async_added_to_hass(self) -> None:
            pass

    ha_helpers_update_coordinator.CoordinatorEntity = MockCoordinatorEntity

    class MockDataUpdateCoordinator:
        def __init__(
            self,
            hass: Any,
            logger: Any,
            name: str,
            update_interval: Any = None,
            always_update: bool = True,
            **kwargs: Any,
        ) -> None:
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval
            self.always_update = always_update
            self.data: dict[str, Any] = {}
            self.last_update_success: bool = True
            self._listeners: list[Callable] = []

        def __class_getitem__(cls, item: Any) -> Any:
            return cls

        def async_add_listener(self, update_callback: Callable, context: Any = None) -> Callable:
            self._listeners.append(update_callback)
            return lambda: self._listeners.remove(update_callback)

        def async_update_listeners(self) -> None:
            for listener in list(self._listeners):
                listener()

        def async_set_updated_data(self, data: dict[str, Any]) -> None:
            self.last_update_success = True
            self.data = data
            self.async_update_listeners()

    ha_helpers_update_coordinator.DataUpdateCoordinator = MockDataUpdateCoordinator
    ha_helpers_update_coordinator.UpdateFailed = Exception

    ha_components = ModuleType("homeassistant.components")
    ha_components.__path__ = []

    ha_components_frontend = ModuleType("homeassistant.components.frontend")
    ha_components_frontend.add_extra_js_url = MagicMock()

    ha_components_http = ModuleType("homeassistant.components.http")
    ha_components_http.StaticPathConfig = MagicMock()

    ha_components_diagnostics = ModuleType("homeassistant.components.diagnostics")
    ha_components_sensor = ModuleType("homeassistant.components.sensor")

    class MockSensorDeviceClass(StrEnum):
        POWER = "power"
        ENERGY = "energy"
        TEMPERATURE = "temperature"
        DURATION = "duration"
        MONETARY = "monetary"

    class MockSensorStateClass(StrEnum):
        MEASUREMENT = "measurement"
        TOTAL = "total"
        TOTAL_INCREASING = "total_increasing"

    from dataclasses import dataclass

    @dataclass(frozen=True, kw_only=True)
    class MockSensorEntityDescription:
        key: str = ""
        name: str | None = None
        native_unit_of_measurement: str | None = None
        device_class: Any = None
        state_class: Any = None
        suggested_display_precision: int | None = None
        icon: str | None = None
        entity_category: Any = None
        translation_key: str | None = None

    class MockSensorEntity:
        @property
        def icon(self) -> str | None:
            return getattr(self, "_attr_icon", None)

    ha_components_sensor.SensorDeviceClass = MockSensorDeviceClass
    ha_components_sensor.SensorStateClass = MockSensorStateClass
    ha_components_sensor.SensorEntityDescription = MockSensorEntityDescription
    ha_components_sensor.SensorEntity = MockSensorEntity

    ha_components_binary_sensor = ModuleType("homeassistant.components.binary_sensor")
    class MockBinarySensorDeviceClass(StrEnum):
        PROBLEM = "problem"
        WINDOW = "window"
        RUNNING = "running"

    @dataclass(frozen=True, kw_only=True)
    class MockBinarySensorEntityDescription:
        key: str = ""
        name: str | None = None
        device_class: Any = None
        translation_key: str | None = None
        icon: str | None = None
        entity_category: Any = None

    class MockBinarySensorEntity:
        pass

    ha_components_binary_sensor.BinarySensorDeviceClass = MockBinarySensorDeviceClass
    ha_components_binary_sensor.BinarySensorEntityDescription = MockBinarySensorEntityDescription
    ha_components_binary_sensor.BinarySensorEntity = MockBinarySensorEntity

    ha_components_button = ModuleType("homeassistant.components.button")
    @dataclass(frozen=True, kw_only=True)
    class MockButtonEntityDescription:
        key: str = ""
        name: str | None = None
        translation_key: str | None = None
        icon: str | None = None
        entity_category: Any = None

    class MockButtonEntity:
        pass

    ha_components_button.ButtonEntityDescription = MockButtonEntityDescription
    ha_components_button.ButtonEntity = MockButtonEntity

    ha_components_number = ModuleType("homeassistant.components.number")
    class MockNumberMode(StrEnum):
        AUTO = "auto"
        BOX = "box"
        SLIDER = "slider"

    @dataclass(frozen=True, kw_only=True)
    class MockNumberEntityDescription:
        key: str = ""
        name: str | None = None
        translation_key: str | None = None
        icon: str | None = None
        native_min_value: float = 0.0
        native_max_value: float = 100.0
        native_step: float = 1.0
        native_unit_of_measurement: str | None = None
        mode: str = "auto"
        entity_category: Any = None

    class MockNumberEntity:
        pass

    ha_components_number.NumberMode = MockNumberMode
    ha_components_number.NumberEntityDescription = MockNumberEntityDescription
    ha_components_number.NumberEntity = MockNumberEntity

    ha_components_select = ModuleType("homeassistant.components.select")
    @dataclass(frozen=True, kw_only=True)
    class MockSelectEntityDescription:
        key: str = ""
        name: str | None = None
        translation_key: str | None = None
        icon: str | None = None
        options: list[str] | None = None
        entity_category: Any = None

    class MockSelectEntity:
        pass

    ha_components_select.SelectEntityDescription = MockSelectEntityDescription
    ha_components_select.SelectEntity = MockSelectEntity

    ha_util = ModuleType("homeassistant.util")
    ha_util.__path__ = []
    ha_util_dt = ModuleType("homeassistant.util.dt")

    # core
    def callback(func: Callable) -> Callable:
        return func

    ha_core.callback = callback
    ha_core.HomeAssistant = MockHomeAssistant
    ha_core.Event = MagicMock
    ha_core.ServiceCall = MagicMock
    ha_core.ServiceResponse = dict[str, Any]
    ha_core.SupportsResponse = MagicMock()
    ha_core.SupportsResponse.OPTIONAL = "optional"

    # config_entries
    class BaseConfigFlow:
        VERSION = 1
        DOMAIN = "thermal_balance"

        def __init_subclass__(cls, domain: str | None = None, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)
            if domain:
                cls.DOMAIN = domain

        def __init__(self) -> None:
            self.hass: Any = None
            self._reconfigure_entry: Any = None
            self.unique_id: str | None = None

        def _get_reconfigure_entry(self) -> Any:
            return self._reconfigure_entry

        async def async_set_unique_id(self, unique_id: str | None = None, *, raise_on_progress: bool = True) -> None:
            self.unique_id = unique_id

        def _abort_if_unique_id_configured(self, updates: dict[str, Any] | None = None, reload_on_update: bool = True) -> None:
            if hasattr(self, "hass") and self.hass and hasattr(self.hass, "config_entries"):
                for entry in self.hass.config_entries.async_entries(getattr(self, "DOMAIN", "thermal_balance")):
                    if getattr(entry, "unique_id", None) == self.unique_id:
                        raise AbortFlow("already_configured")

        def async_show_form(self, step_id: str, data_schema: Any, errors: dict[str, str] | None = None) -> dict[str, Any]:
            return {"type": "form", "step_id": step_id, "data_schema": data_schema, "errors": errors or {}}

        def async_create_entry(self, title: str, data: dict[str, Any]) -> dict[str, Any]:
            return {"type": "create_entry", "title": title, "data": data}

        def async_abort(self, *, reason: str, description_placeholders: dict[str, str] | None = None) -> dict[str, Any]:
            return {"type": "abort", "reason": reason}

        def async_update_reload_and_abort(self, entry: Any, data: dict[str, Any], reason: str) -> dict[str, Any]:
            return {"type": "abort", "reason": reason, "data": data}

    class BaseOptionsFlow:
        def __init__(self, config_entry: Any = None) -> None:
            if config_entry is not None:
                self.config_entry = config_entry

        def async_show_form(self, step_id: str, data_schema: Any, errors: dict[str, str] | None = None) -> dict[str, Any]:
            return {"type": "form", "step_id": step_id, "data_schema": data_schema, "errors": errors or {}}

        def async_create_entry(self, title: str, data: dict[str, Any]) -> dict[str, Any]:
            return {"type": "create_entry", "title": title, "data": data}

    class AbortFlow(Exception):
        def __init__(self, reason: str, description_placeholders: dict[str, str] | None = None) -> None:
            super().__init__(reason)
            self.reason = reason
            self.description_placeholders = description_placeholders

    ha_data_entry_flow = ModuleType("homeassistant.data_entry_flow")
    ha_data_entry_flow.AbortFlow = AbortFlow
    ha_config_entries.AbortFlow = AbortFlow
    ha_config_entries.ConfigFlow = BaseConfigFlow
    ha_config_entries.OptionsFlow = BaseOptionsFlow
    ha_config_entries.ConfigEntry = MockConfigEntry
    ha_config_entries.ConfigFlowResult = dict[str, Any]

    # helpers.selector
    class MockSelector:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def __call__(self, data: Any) -> Any:
            return data

    ha_helpers_selector.NumberSelector = MockSelector
    ha_helpers_selector.NumberSelectorConfig = MockSelector
    ha_helpers_selector.NumberSelectorMode = MagicMock()
    ha_helpers_selector.NumberSelectorMode.BOX = "box"
    ha_helpers_selector.SelectSelector = MockSelector
    ha_helpers_selector.SelectSelectorConfig = MockSelector
    ha_helpers_selector.SelectSelectorMode = MagicMock()
    ha_helpers_selector.SelectSelectorMode.DROPDOWN = "dropdown"
    ha_helpers_selector.SelectOptionDict = dict
    ha_helpers_selector.EntitySelector = MockSelector
    ha_helpers_selector.EntitySelectorConfig = MockSelector
    ha_helpers_selector.BooleanSelector = MockSelector
    ha_helpers_selector.TextSelector = MockSelector

    # helpers.event
    def mock_track_state_change_event(hass: Any, entities: Any, callback: Any) -> Callable:
        return lambda: None

    def mock_track_time_change(hass: Any, callback: Any, hour: int = 0, minute: int = 0, second: int = 0) -> Callable:
        return lambda: None

    def mock_track_time_interval(hass: Any, callback: Any, interval: Any) -> Callable:
        return lambda: None

    ha_helpers_event.async_track_state_change_event = mock_track_state_change_event
    ha_helpers_event.async_track_time_change = mock_track_time_change
    ha_helpers_event.async_track_time_interval = mock_track_time_interval

    # util.dt
    ha_util_dt.now = lambda: datetime.now(timezone.utc)
    ha_util_dt.utcnow = lambda: datetime.now(timezone.utc)
    ha_util_dt.DEFAULT_TIME_ZONE = timezone.utc

    # components.diagnostics
    def async_redact_data(data: dict[str, Any], to_redact: list[str]) -> dict[str, Any]:
        return {k: v for k, v in data.items() if k not in to_redact}

    ha_components_diagnostics.async_redact_data = async_redact_data

    # exceptions
    ha_exceptions = ModuleType("homeassistant.exceptions")

    class HomeAssistantError(Exception):
        """General Home Assistant exception."""

    class ServiceValidationError(HomeAssistantError):
        """Action/service validation exception with translation support."""

        def __init__(
            self,
            message: str,
            *,
            translation_domain: str | None = None,
            translation_key: str | None = None,
            translation_placeholders: dict[str, str] | None = None,
        ) -> None:
            super().__init__(message)
            self.translation_domain = translation_domain
            self.translation_key = translation_key
            self.translation_placeholders = translation_placeholders

    ha_exceptions.HomeAssistantError = HomeAssistantError
    ha_exceptions.ServiceValidationError = ServiceValidationError

    # Register in sys.modules
    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.exceptions"] = ha_exceptions
    sys.modules["homeassistant.const"] = ha_const
    sys.modules["homeassistant.core"] = ha_core
    sys.modules["homeassistant.config_entries"] = ha_config_entries
    sys.modules["homeassistant.helpers"] = ha_helpers
    sys.modules["homeassistant.helpers.typing"] = ha_helpers_typing
    sys.modules["homeassistant.helpers.config_validation"] = ha_helpers_cv
    sys.modules["homeassistant.helpers.selector"] = ha_helpers_selector
    sys.modules["homeassistant.helpers.event"] = ha_helpers_event
    sys.modules["homeassistant.helpers.entity"] = ha_helpers_entity
    sys.modules["homeassistant.helpers.entity_platform"] = ha_helpers_entity_platform
    sys.modules["homeassistant.helpers.restore_state"] = ha_helpers_restore_state
    sys.modules["homeassistant.helpers.update_coordinator"] = ha_helpers_update_coordinator
    sys.modules["homeassistant.components"] = ha_components
    sys.modules["homeassistant.components.frontend"] = ha_components_frontend
    sys.modules["homeassistant.components.http"] = ha_components_http
    sys.modules["homeassistant.components.diagnostics"] = ha_components_diagnostics
    sys.modules["homeassistant.components.sensor"] = ha_components_sensor
    sys.modules["homeassistant.components.binary_sensor"] = ha_components_binary_sensor
    sys.modules["homeassistant.components.button"] = ha_components_button
    sys.modules["homeassistant.components.number"] = ha_components_number
    sys.modules["homeassistant.components.select"] = ha_components_select
    sys.modules["homeassistant.data_entry_flow"] = ha_data_entry_flow
    sys.modules["homeassistant.util"] = ha_util
    sys.modules["homeassistant.util.dt"] = ha_util_dt
