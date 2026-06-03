use buddy_domain::{BoardKind, BootloaderMode, McuKind, ProductProfile};

const STM32F407_BOOT_STARTUP_PATHS: &[&str] = &[
    "src/device/stm32f4/startup/CMakeLists.txt",
    "src/device/stm32f4/startup/stm32f407xx_boot.s",
    "src/device/stm32f4/cmsis_boot.cpp",
];
const STM32F407_NOBOOT_STARTUP_PATHS: &[&str] = &[
    "src/device/stm32f4/startup/CMakeLists.txt",
    "src/device/stm32f4/startup/stm32f407xx.s",
    "src/device/stm32f4/cmsis.cpp",
];
const STM32F42_BOOT_STARTUP_PATHS: &[&str] = &[
    "src/device/stm32f4/startup/CMakeLists.txt",
    "src/device/stm32f4/startup/stm32f427zitx_boot.s",
    "src/device/stm32f4/cmsis_boot.cpp",
];
const STM32F42_NOBOOT_STARTUP_PATHS: &[&str] = &[
    "src/device/stm32f4/startup/CMakeLists.txt",
    "src/device/stm32f4/startup/stm32f427zitx.s",
    "src/device/stm32f4/cmsis.cpp",
];
const STM32G0_STARTUP_PATHS: &[&str] = &[
    "src/device/stm32g0/startup/CMakeLists.txt",
    "src/device/stm32g0/startup/stm32g070xx.s",
    "src/device/stm32g0/cmsis.cpp",
    "src/device/stm32g0/core_init.cpp",
];
const STM32H503_XBUDDY_EXTENSION_STARTUP_PATHS: &[&str] = &[
    "src/puppy/xbuddy_extension/CMakeLists.txt",
    "src/puppy/xbuddy_extension/stm32h503.s",
    "src/puppy/xbuddy_extension/cmsis.cpp",
    "src/puppy/xbuddy_extension/hal_clock.cpp",
];
const ALL_EVIDENCE_CLASSES: &[EvidenceClass] = &[
    EvidenceClass::ManifestCheck,
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::BazelQuery,
    EvidenceClass::SimulatorFlow,
    EvidenceClass::HardwareSmoke,
    EvidenceClass::ManualHardwareRequired,
];
const H503_TOOLCHAIN_EVIDENCE: &[&str] = &[
    "Cortex-M33",
    "fpv5-sp-d16",
    "exact production Bazel platform/toolchain labels deferred to later build-system refinement",
];
const NO_FPU_EVIDENCE: &[&str] = &["no FPU evidence required for this startup contract"];

/// Evidence class for runtime-boundary claims.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum EvidenceClass {
    /// Machine-readable manifest coverage.
    ManifestCheck,
    /// Local static source or manifest audit.
    StaticSourceAudit,
    /// Host Rust unit tests for contract logic.
    RustHostTest,
    /// Queryable Bazel label coverage.
    BazelQuery,
    /// Simulator validation required for runtime behavior.
    SimulatorFlow,
    /// Hardware smoke validation required for runtime behavior.
    HardwareSmoke,
    /// Manual hardware evidence is still required before claiming parity.
    ManualHardwareRequired,
}

impl EvidenceClass {
    /// Returns the manifest spelling used by Phase 5 audit rows.
    pub fn audit_value(self) -> &'static str {
        match self {
            Self::ManifestCheck => "manifest-check",
            Self::StaticSourceAudit => "static-source-audit",
            Self::RustHostTest => "rust-host-test",
            Self::BazelQuery => "bazel-query",
            Self::SimulatorFlow => "simulator-flow",
            Self::HardwareSmoke => "hardware-smoke",
            Self::ManualHardwareRequired => "manual-hardware-required",
        }
    }

    /// Returns true when the evidence is not a local host proof.
    pub fn requires_non_local_runtime_evidence(self) -> bool {
        matches!(
            self,
            Self::SimulatorFlow | Self::HardwareSmoke | Self::ManualHardwareRequired
        )
    }
}

/// Startup vector-table contract for a retained startup owner.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StartupVectorTable {
    retained_component_id: &'static str,
    source_evidence_paths: &'static [&'static str],
    vector_symbol: &'static str,
    reset_handler_symbol: &'static str,
    vector_section: &'static str,
    maybe_fpu_evidence: Option<&'static str>,
}

impl StartupVectorTable {
    /// Returns the retained foreign-code inventory row that owns this table.
    pub fn retained_component_id(&self) -> &'static str {
        self.retained_component_id
    }

    /// Returns startup source paths that provide vector-table evidence.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        self.source_evidence_paths
    }

    /// Returns the retained vector-table symbol.
    pub fn vector_symbol(&self) -> &'static str {
        self.vector_symbol
    }

    /// Returns the retained reset-handler symbol.
    pub fn reset_handler_symbol(&self) -> &'static str {
        self.reset_handler_symbol
    }

    /// Returns the linker section that owns the vector table.
    pub fn vector_section(&self) -> &'static str {
        self.vector_section
    }

    /// Returns FPU evidence when the selected retained startup surface needs it.
    pub fn maybe_fpu_evidence(&self) -> Option<&'static str> {
        self.maybe_fpu_evidence
    }
}

/// Startup surface selected from a validated product profile.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StartupSurface {
    retained_component_id: &'static str,
    vector_table: StartupVectorTable,
    board_clock_contract_id: &'static str,
    evidence_classes: &'static [EvidenceClass],
    toolchain_evidence_notes: &'static [&'static str],
}

impl StartupSurface {
    /// Creates a startup surface contract without mutating retained startup code.
    pub fn from_profile(profile: &ProductProfile) -> Self {
        let vector_table =
            vector_table_for(profile.board(), profile.mcu(), profile.bootloader_mode());
        let toolchain_evidence_notes = if profile.mcu() == McuKind::Stm32H503CbU7 {
            H503_TOOLCHAIN_EVIDENCE
        } else {
            NO_FPU_EVIDENCE
        };

        Self {
            retained_component_id: vector_table.retained_component_id(),
            vector_table,
            board_clock_contract_id: "board-clock-tree-contracts",
            evidence_classes: ALL_EVIDENCE_CLASSES,
            toolchain_evidence_notes,
        }
    }

    /// Returns the retained foreign-code inventory row that owns this surface.
    pub fn retained_component_id(&self) -> &'static str {
        self.retained_component_id
    }

    /// Returns the retained startup vector-table contract.
    pub fn startup_vector_table(&self) -> StartupVectorTable {
        self.vector_table
    }

    /// Returns the audit surface that owns board-clock evidence.
    pub fn board_clock_contract_id(&self) -> &'static str {
        self.board_clock_contract_id
    }

    /// Returns local and non-local evidence classes for this contract.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        self.evidence_classes
    }

    /// Returns FPU evidence when the selected retained startup surface needs it.
    pub fn maybe_fpu_evidence(&self) -> Option<&'static str> {
        self.vector_table.maybe_fpu_evidence()
    }

    /// Returns toolchain notes that prevent overclaiming local hardware proof.
    pub fn toolchain_evidence_notes(&self) -> &'static [&'static str] {
        self.toolchain_evidence_notes
    }
}

fn vector_table_for(
    board: BoardKind,
    mcu: McuKind,
    bootloader_mode: BootloaderMode,
) -> StartupVectorTable {
    let (retained_component_id, source_evidence_paths, maybe_fpu_evidence) = match (board, mcu) {
        (BoardKind::XBuddyExtension, McuKind::Stm32H503CbU7) => (
            "stm32h503-xbuddy-extension-startup-linker",
            STM32H503_XBUDDY_EXTENSION_STARTUP_PATHS,
            Some("fpv5-sp-d16"),
        ),
        (BoardKind::Dwarf | BoardKind::ModularBed, McuKind::Stm32G070RbT6) => {
            ("stm32g0-startup-linker", STM32G0_STARTUP_PATHS, None)
        }
        (_, McuKind::Stm32G070RbT6) => ("stm32g0-startup-linker", STM32G0_STARTUP_PATHS, None),
        (_, McuKind::Stm32F407Vg) => (
            "stm32f4-startup-linker",
            f407_startup_paths(bootloader_mode),
            None,
        ),
        (_, McuKind::Stm32F427Zi | McuKind::Stm32F429Vi) => (
            "stm32f4-startup-linker",
            f42_startup_paths(bootloader_mode),
            None,
        ),
        (_, McuKind::Stm32H503CbU7) => (
            "stm32h503-xbuddy-extension-startup-linker",
            STM32H503_XBUDDY_EXTENSION_STARTUP_PATHS,
            Some("fpv5-sp-d16"),
        ),
    };

    StartupVectorTable {
        retained_component_id,
        source_evidence_paths,
        vector_symbol: "g_pfnVectors",
        reset_handler_symbol: "Reset_Handler",
        vector_section: ".isr_vector",
        maybe_fpu_evidence,
    }
}

fn f407_startup_paths(bootloader_mode: BootloaderMode) -> &'static [&'static str] {
    match bootloader_mode {
        BootloaderMode::Boot => STM32F407_BOOT_STARTUP_PATHS,
        BootloaderMode::NoBoot | BootloaderMode::Auxiliary => STM32F407_NOBOOT_STARTUP_PATHS,
    }
}

fn f42_startup_paths(bootloader_mode: BootloaderMode) -> &'static [&'static str] {
    match bootloader_mode {
        BootloaderMode::Boot => STM32F42_BOOT_STARTUP_PATHS,
        BootloaderMode::NoBoot | BootloaderMode::Auxiliary => STM32F42_NOBOOT_STARTUP_PATHS,
    }
}

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
    fn f4_profiles_select_f4_startup_evidence() {
        // Arrange
        let boot_profile = profile(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );
        let noboot_profile = profile(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::NoBoot,
            FeatureSet::empty(),
        );

        // Act
        let boot_surface = StartupSurface::from_profile(&boot_profile);
        let noboot_surface = StartupSurface::from_profile(&noboot_profile);

        // Assert
        assert!(
            boot_surface
                .startup_vector_table()
                .source_evidence_paths()
                .contains(&"src/device/stm32f4/startup/stm32f407xx_boot.s")
        );
        assert!(
            noboot_surface
                .startup_vector_table()
                .source_evidence_paths()
                .contains(&"src/device/stm32f4/startup/stm32f407xx.s")
        );
        assert!(
            !boot_surface
                .startup_vector_table()
                .source_evidence_paths()
                .contains(&"src/puppy/xbuddy_extension/stm32h503.s")
        );
    }

    #[test]
    fn g0_auxiliary_profile_selects_g0_startup_evidence() {
        // Arrange
        let profile = profile(
            PrinterKind::Xl,
            BoardKind::Dwarf,
            McuKind::Stm32G070RbT6,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::Dwarf]),
        );

        // Act
        let surface = StartupSurface::from_profile(&profile);

        // Assert
        assert!(
            surface
                .startup_vector_table()
                .source_evidence_paths()
                .contains(&"src/device/stm32g0/startup/stm32g070xx.s")
        );
        assert_eq!(surface.retained_component_id(), "stm32g0-startup-linker");
    }

    #[test]
    fn h503_profile_exposes_xbuddy_extension_startup_evidence() {
        // Arrange
        let profile = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddyExtension,
            McuKind::Stm32H503CbU7,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::XBuddyExtension]),
        );

        // Act
        let surface = StartupSurface::from_profile(&profile);

        // Assert
        assert!(
            surface
                .startup_vector_table()
                .source_evidence_paths()
                .contains(&"src/puppy/xbuddy_extension/stm32h503.s")
        );
        assert_eq!(surface.maybe_fpu_evidence(), Some("fpv5-sp-d16"));
        assert!(
            surface
                .toolchain_evidence_notes()
                .contains(&"exact production Bazel platform/toolchain labels deferred to later build-system refinement")
        );
    }

    #[test]
    fn startup_evidence_keeps_non_local_hardware_classes() {
        // Arrange
        let profile = profile(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );

        // Act
        let surface = StartupSurface::from_profile(&profile);

        // Assert
        assert!(
            surface
                .evidence_classes()
                .contains(&EvidenceClass::ManualHardwareRequired)
        );
        assert!(
            surface
                .evidence_classes()
                .contains(&EvidenceClass::SimulatorFlow)
        );
        assert!(
            surface
                .evidence_classes()
                .contains(&EvidenceClass::HardwareSmoke)
        );
        assert!(EvidenceClass::ManualHardwareRequired.requires_non_local_runtime_evidence());
    }
}
