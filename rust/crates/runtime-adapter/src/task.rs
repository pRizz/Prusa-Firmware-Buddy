use crate::EvidenceClass;
use buddy_domain::{Feature, ProductProfile};

const TASK_SOURCE_EVIDENCE: &[&str] = &[
    "include/tasks.hpp",
    "src/common/tasks.cpp",
    "src/buddy/main.cpp",
    "src/common/appmain.cpp",
    "src/puppies/puppy_task.cpp",
    "src/puppy/dwarf/main.cpp",
    "src/puppy/modularbed/main.cpp",
    "src/puppy/xbuddy_extension/main.cpp",
];
const TASK_EVIDENCE: &[EvidenceClass] = &[
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::SimulatorFlow,
    EvidenceClass::HardwareSmoke,
    EvidenceClass::ManualHardwareRequired,
];

/// Task dependency names from `TaskDeps::Dependency`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum TaskDependency {
    PuppiesReady,
    ResourcesReady,
    UsbDeviceReady,
    DefaultTaskReady,
    EspFlashed,
    NetworkingReady,
    UsbTempGuiReady,
    GuiDisplayReady,
    GuiReady,
}

impl TaskDependency {
    /// Returns all retained dependency names in enum order.
    pub fn all() -> &'static [Self] {
        ALL_TASK_DEPENDENCIES
    }

    /// Returns the exact retained C++ enum spelling.
    pub fn name(self) -> &'static str {
        match self {
            Self::PuppiesReady => "puppies_ready",
            Self::ResourcesReady => "resources_ready",
            Self::UsbDeviceReady => "usb_device_ready",
            Self::DefaultTaskReady => "default_task_ready",
            Self::EspFlashed => "esp_flashed",
            Self::NetworkingReady => "networking_ready",
            Self::UsbTempGuiReady => "usb_temp_gui_ready",
            Self::GuiDisplayReady => "gui_display_ready",
            Self::GuiReady => "gui_ready",
        }
    }

    /// Returns the `TaskDeps::make` bit for this dependency.
    pub fn bit(self) -> u32 {
        1_u32 << self.bit_index()
    }

    fn bit_index(self) -> u32 {
        match self {
            Self::PuppiesReady => 0,
            Self::ResourcesReady => 1,
            Self::UsbDeviceReady => 2,
            Self::DefaultTaskReady => 3,
            Self::EspFlashed => 4,
            Self::NetworkingReady => 5,
            Self::UsbTempGuiReady => 6,
            Self::GuiDisplayReady => 7,
            Self::GuiReady => 8,
        }
    }
}

const ALL_TASK_DEPENDENCIES: &[TaskDependency] = &[
    TaskDependency::PuppiesReady,
    TaskDependency::ResourcesReady,
    TaskDependency::UsbDeviceReady,
    TaskDependency::DefaultTaskReady,
    TaskDependency::EspFlashed,
    TaskDependency::NetworkingReady,
    TaskDependency::UsbTempGuiReady,
    TaskDependency::GuiDisplayReady,
    TaskDependency::GuiReady,
];

/// Whether a zero dependency mask is allowed by the retained build configuration.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DependencyMaskRequirement {
    /// A zero mask is allowed, matching feature-gated `TaskDeps::make(...)` call sites.
    AllowEmpty,
    /// At least one dependency bit is required.
    RequireNonEmpty,
}

/// Error returned when a dependency mask cannot represent a valid contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DependencyMaskError {
    /// The caller required a non-empty mask, but the mask was zero.
    EmptyMask,
}

/// Typed wrapper for a FreeRTOS event-group dependency mask.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DependencyMask {
    bits: u32,
}

impl DependencyMask {
    /// Creates a dependency mask and optionally rejects an empty mask.
    pub fn new(
        bits: u32,
        requirement: DependencyMaskRequirement,
    ) -> Result<Self, DependencyMaskError> {
        if bits == 0 && requirement == DependencyMaskRequirement::RequireNonEmpty {
            return Err(DependencyMaskError::EmptyMask);
        }

        Ok(Self { bits })
    }

    /// Creates a mask from typed dependency names.
    pub fn from_dependencies(
        dependencies: &[TaskDependency],
        requirement: DependencyMaskRequirement,
    ) -> Result<Self, DependencyMaskError> {
        let bits = dependencies
            .iter()
            .fold(0_u32, |mask, dependency| mask | dependency.bit());

        Self::new(bits, requirement)
    }

    /// Returns the raw retained `EventBits_t` mask value.
    pub fn bits(self) -> u32 {
        self.bits
    }

    /// Returns true when this mask contains the dependency bit.
    pub fn contains(self, dependency: TaskDependency) -> bool {
        (self.bits & dependency.bit()) == dependency.bit()
    }
}

/// Runtime task or startup personality represented by a task contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RuntimeTask {
    UsbDevice,
    DefaultTask,
    MarlinClient,
    PuppyRuntime,
    ConnectClient,
    Syslog,
    Network,
    Bootstrap,
    MasterStartup,
    DwarfStartup,
    ModularBedStartup,
    XBuddyExtensionStartup,
}

impl RuntimeTask {
    /// Returns the retained runtime-personality name.
    pub fn name(self) -> &'static str {
        match self {
            Self::UsbDevice => "usb_device",
            Self::DefaultTask => "default_task",
            Self::MarlinClient => "marlin_client",
            Self::PuppyRuntime => "puppy_runtime",
            Self::ConnectClient => "connect_client",
            Self::Syslog => "syslog",
            Self::Network => "network",
            Self::Bootstrap => "bootstrap",
            Self::MasterStartup => "master_startup",
            Self::DwarfStartup => "dwarf_startup",
            Self::ModularBedStartup => "modular_bed_startup",
            Self::XBuddyExtensionStartup => "xbuddy_extension_startup",
        }
    }
}

/// Startup-order and task-dependency contract for retained runtime tasks.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct TaskStartupContract {
    name: &'static str,
    runtime_task: RuntimeTask,
    dependencies: &'static [TaskDependency],
    dependency_requirement: DependencyMaskRequirement,
    startup_order: &'static str,
    source_evidence_paths: &'static [&'static str],
    audit_surface_id: &'static str,
    evidence_classes: &'static [EvidenceClass],
}

impl TaskStartupContract {
    /// Returns the known retained task dependency contracts.
    pub fn known_contracts() -> &'static [Self] {
        KNOWN_TASK_CONTRACTS
    }

    /// Returns the contract with the exact retained name, if one is known.
    pub fn maybe_named(name: &str) -> Option<&'static Self> {
        KNOWN_TASK_CONTRACTS
            .iter()
            .find(|contract| contract.name == name)
    }

    /// Returns the exact retained `TaskDeps::Tasks` name.
    pub fn name(&self) -> &'static str {
        self.name
    }

    /// Returns the task or runtime personality that consumes this contract.
    pub fn runtime_task(&self) -> RuntimeTask {
        self.runtime_task
    }

    /// Returns feature-inclusive dependency names used as retained evidence.
    ///
    /// Use `dependencies_for_profile` when building the effective retained mask
    /// for a concrete product profile.
    pub fn dependencies(&self) -> &'static [TaskDependency] {
        self.dependencies
    }

    /// Returns typed dependency names after applying retained feature gates.
    pub fn dependencies_for_profile(&self, profile: &ProductProfile) -> &'static [TaskDependency] {
        let has_puppies = profile.features().contains(Feature::Puppies);
        match self.name {
            "default_start" if !has_puppies => EMPTY_STARTUP_DEPS,
            "bootstrap_done" if !has_puppies => BOOTSTRAP_DONE_BASE_DEPS,
            _ => self.dependencies,
        }
    }

    /// Returns the dependency mask for this contract and product profile.
    pub fn dependency_mask(
        &self,
        profile: &ProductProfile,
    ) -> Result<DependencyMask, DependencyMaskError> {
        DependencyMask::from_dependencies(
            self.dependencies_for_profile(profile),
            self.dependency_requirement,
        )
    }

    /// Returns startup-order evidence from retained C/C++ entrypoints.
    pub fn startup_order(&self) -> &'static str {
        self.startup_order
    }

    /// Returns source paths proving retained task dependency behavior.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        self.source_evidence_paths
    }

    /// Returns the Phase 5 unsafe-audit surface ID for readiness behavior.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }

    /// Returns evidence classes for this task contract.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        self.evidence_classes
    }
}

const DEFAULT_START_DEPS_WITH_PUPPIES: &[TaskDependency] = &[TaskDependency::PuppiesReady];
const USB_DEVICE_START_DEPS: &[TaskDependency] = &[TaskDependency::UsbDeviceReady];
const DEFAULT_TASK_READY_DEPS: &[TaskDependency] = &[TaskDependency::DefaultTaskReady];
const BOOTSTRAP_DONE_BASE_DEPS: &[TaskDependency] =
    &[TaskDependency::ResourcesReady, TaskDependency::EspFlashed];
const BOOTSTRAP_DONE_DEPS_WITH_PUPPIES: &[TaskDependency] = &[
    TaskDependency::ResourcesReady,
    TaskDependency::EspFlashed,
    TaskDependency::PuppiesReady,
];
const NETWORKING_READY_DEPS: &[TaskDependency] = &[TaskDependency::NetworkingReady];
const ESP_FLASHED_DEPS: &[TaskDependency] = &[TaskDependency::EspFlashed];
const GUI_DISPLAY_DEPS: &[TaskDependency] = &[TaskDependency::GuiDisplayReady];
const EMPTY_STARTUP_DEPS: &[TaskDependency] = &[];

const KNOWN_TASK_CONTRACTS: &[TaskStartupContract] = &[
    TaskStartupContract {
        name: "usb_device_start",
        runtime_task: RuntimeTask::UsbDevice,
        dependencies: USB_DEVICE_START_DEPS,
        dependency_requirement: DependencyMaskRequirement::RequireNonEmpty,
        startup_order: "appmain waits for USB device readiness before binding SerialUSB when HAS_USB_DEVICE is enabled",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "default_start",
        runtime_task: RuntimeTask::DefaultTask,
        dependencies: DEFAULT_START_DEPS_WITH_PUPPIES,
        dependency_requirement: DependencyMaskRequirement::AllowEmpty,
        startup_order: "default task waits for puppies_ready only when HAS_PUPPIES gates the retained mask",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "marlin_client",
        runtime_task: RuntimeTask::MarlinClient,
        dependencies: DEFAULT_TASK_READY_DEPS,
        dependency_requirement: DependencyMaskRequirement::RequireNonEmpty,
        startup_order: "Marlin clients wait for default_task_ready after marlin_server initialization",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "puppy_run",
        runtime_task: RuntimeTask::PuppyRuntime,
        dependencies: DEFAULT_TASK_READY_DEPS,
        dependency_requirement: DependencyMaskRequirement::RequireNonEmpty,
        startup_order: "puppy task waits for default_task_ready before entering runtime refresh loops",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "bootstrap_done",
        runtime_task: RuntimeTask::Bootstrap,
        dependencies: BOOTSTRAP_DONE_DEPS_WITH_PUPPIES,
        dependency_requirement: DependencyMaskRequirement::RequireNonEmpty,
        startup_order: "bootstrap waits for resources_ready and esp_flashed plus puppies_ready when retained feature gates enable puppies",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "connect",
        runtime_task: RuntimeTask::ConnectClient,
        dependencies: NETWORKING_READY_DEPS,
        dependency_requirement: DependencyMaskRequirement::RequireNonEmpty,
        startup_order: "Connect starts only after networking_ready is provided by retained WUI/network startup",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "syslog",
        runtime_task: RuntimeTask::Syslog,
        dependencies: NETWORKING_READY_DEPS,
        dependency_requirement: DependencyMaskRequirement::RequireNonEmpty,
        startup_order: "syslog reconfiguration waits for networking_ready before metrics/syslog output",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "network",
        runtime_task: RuntimeTask::Network,
        dependencies: ESP_FLASHED_DEPS,
        dependency_requirement: DependencyMaskRequirement::RequireNonEmpty,
        startup_order: "network task creation waits until ESP flashing has completed or been skipped",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "bootstrap_start",
        runtime_task: RuntimeTask::Bootstrap,
        dependencies: GUI_DISPLAY_DEPS,
        dependency_requirement: DependencyMaskRequirement::RequireNonEmpty,
        startup_order: "resource/bootstrap progress waits for GUI display readiness before taking over progress UI",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "puppy_task_start",
        runtime_task: RuntimeTask::PuppyRuntime,
        dependencies: ESP_FLASHED_DEPS,
        dependency_requirement: DependencyMaskRequirement::RequireNonEmpty,
        startup_order: "puppy task body waits for esp_flashed before puppy bootstrap and scan",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "dwarf_startup",
        runtime_task: RuntimeTask::DwarfStartup,
        dependencies: EMPTY_STARTUP_DEPS,
        dependency_requirement: DependencyMaskRequirement::AllowEmpty,
        startup_order: "Dwarf startup creates a startup task before osKernelStart without TaskDeps event bits",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "modular_bed_startup",
        runtime_task: RuntimeTask::ModularBedStartup,
        dependencies: EMPTY_STARTUP_DEPS,
        dependency_requirement: DependencyMaskRequirement::AllowEmpty,
        startup_order: "ModularBed initializes HAL, watchdog, Modbus, and control tasks before osKernelStart",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
    TaskStartupContract {
        name: "xbuddy_extension_startup",
        runtime_task: RuntimeTask::XBuddyExtensionStartup,
        dependencies: EMPTY_STARTUP_DEPS,
        dependency_requirement: DependencyMaskRequirement::AllowEmpty,
        startup_order: "xBuddy Extension creates static main and HAL tasks before vTaskStartScheduler with MPU regions",
        source_evidence_paths: TASK_SOURCE_EVIDENCE,
        audit_surface_id: "task-dependency-readiness",
        evidence_classes: TASK_EVIDENCE,
    },
];

#[cfg(test)]
mod tests {
    use super::*;
    use buddy_domain::{
        BoardKind, BootloaderMode, Feature, FeatureSet, McuKind, PrinterKind, ProductProfile,
    };

    fn profile(
        printer: PrinterKind,
        board: BoardKind,
        mcu: McuKind,
        bootloader_mode: BootloaderMode,
        features: FeatureSet,
    ) -> ProductProfile {
        ProductProfile::new(printer, board, mcu, bootloader_mode, features)
            .expect("test profile must match the supported product matrix")
    }

    #[test]
    fn dependency_mask_rejects_zero_only_when_non_empty_required() {
        // Arrange, Act
        let maybe_empty = DependencyMask::new(0, DependencyMaskRequirement::AllowEmpty);
        let required = DependencyMask::new(0, DependencyMaskRequirement::RequireNonEmpty);

        // Assert
        assert!(maybe_empty.is_ok());
        assert_eq!(required, Err(DependencyMaskError::EmptyMask));
    }

    #[test]
    fn named_task_contracts_include_reference_taskdeps_masks() {
        // Arrange
        let expected_names = [
            "default_start",
            "network",
            "connect",
            "syslog",
            "bootstrap_done",
            "puppy_task_start",
        ];

        // Act
        let contracts = TaskStartupContract::known_contracts();

        // Assert
        for expected_name in expected_names {
            assert!(
                contracts
                    .iter()
                    .any(|contract| contract.name() == expected_name),
                "missing {expected_name}"
            );
        }
    }

    #[test]
    fn non_puppy_profile_drops_puppies_from_feature_gated_masks() {
        // Arrange
        let profile = profile(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );
        let default_start =
            TaskStartupContract::maybe_named("default_start").expect("default_start is known");
        let bootstrap_done =
            TaskStartupContract::maybe_named("bootstrap_done").expect("bootstrap_done is known");

        // Act
        let default_start_mask = default_start
            .dependency_mask(&profile)
            .expect("default_start may be empty when puppies are disabled");
        let bootstrap_done_mask = bootstrap_done
            .dependency_mask(&profile)
            .expect("bootstrap_done keeps base resources and ESP dependencies");

        // Assert
        assert_eq!(default_start_mask.bits(), 0);
        assert!(!bootstrap_done_mask.contains(TaskDependency::PuppiesReady));
        assert!(bootstrap_done_mask.contains(TaskDependency::ResourcesReady));
        assert!(bootstrap_done_mask.contains(TaskDependency::EspFlashed));
    }

    #[test]
    fn puppy_profile_keeps_puppies_in_feature_gated_masks() {
        // Arrange
        let profile = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddy,
            McuKind::Stm32F427Zi,
            BootloaderMode::Boot,
            FeatureSet::from_features([Feature::Puppies]),
        );
        let default_start =
            TaskStartupContract::maybe_named("default_start").expect("default_start is known");
        let bootstrap_done =
            TaskStartupContract::maybe_named("bootstrap_done").expect("bootstrap_done is known");

        // Act
        let default_start_mask = default_start
            .dependency_mask(&profile)
            .expect("default_start waits for puppies on puppy-enabled profiles");
        let bootstrap_done_mask = bootstrap_done
            .dependency_mask(&profile)
            .expect("bootstrap_done keeps puppies on puppy-enabled profiles");

        // Assert
        assert!(default_start_mask.contains(TaskDependency::PuppiesReady));
        assert!(bootstrap_done_mask.contains(TaskDependency::PuppiesReady));
        assert!(bootstrap_done_mask.contains(TaskDependency::ResourcesReady));
        assert!(bootstrap_done_mask.contains(TaskDependency::EspFlashed));
    }
}
