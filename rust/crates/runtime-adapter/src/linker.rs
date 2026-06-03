use crate::EvidenceClass;
use buddy_domain::{BoardKind, BootloaderMode, McuKind, ProductProfile};

const STM32F407_LINKER_SCRIPTS: &[&str] = &[
    "src/device/stm32f4/linker/stm32f407vg_boot.ld",
    "src/device/stm32f4/linker/stm32f407vg.ld",
];
const STM32F42_LINKER_SCRIPTS: &[&str] = &[
    "src/device/stm32f4/linker/stm32f42x_boot.ld",
    "src/device/stm32f4/linker/stm32f42x.ld",
];
const STM32G0_LINKER_SCRIPTS: &[&str] = &[
    "src/device/stm32g0/linker/stm32g070rb_boot.ld",
    "src/device/stm32g0/linker/stm32g070rb.ld",
];
const STM32H503_XBUDDY_EXTENSION_LINKER_SCRIPTS: &[&str] = &[
    "src/puppy/xbuddy_extension/stm32h503_boot.ld",
    "src/puppy/xbuddy_extension/stm32h503_noboot.ld",
    "src/puppy/xbuddy_extension/stm32h503.ld",
];
const LINKER_EVIDENCE_CLASSES: &[EvidenceClass] = &[
    EvidenceClass::ManifestCheck,
    EvidenceClass::StaticSourceAudit,
    EvidenceClass::RustHostTest,
    EvidenceClass::SimulatorFlow,
    EvidenceClass::HardwareSmoke,
    EvidenceClass::ManualHardwareRequired,
];
const COMMON_LINKER_SECTIONS: &[LinkerSection] = &[
    LinkerSection::new(".isr_vector", "startup-vector-contracts"),
    LinkerSection::new(".text", "linker-section-contracts"),
    LinkerSection::new(".data", "mutable-static-boundary"),
    LinkerSection::new(".bss", "mutable-static-boundary"),
    LinkerSection::new("._user_heap_stack", "allocator-heap-contracts"),
];
const H503_LINKER_SECTIONS: &[LinkerSection] = &[
    LinkerSection::new(".isr_vector", "startup-vector-contracts"),
    LinkerSection::new(".text", "linker-section-contracts"),
    LinkerSection::new(".data", "mutable-static-boundary"),
    LinkerSection::new(".bss", "mutable-static-boundary"),
    LinkerSection::new("._user_heap_stack", "allocator-heap-contracts"),
    LinkerSection::new(".fw_descriptor", "linker-section-contracts"),
];

/// Linker section named by retained scripts and audit surfaces.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct LinkerSection {
    name: &'static str,
    audit_surface_id: &'static str,
}

impl LinkerSection {
    /// Creates a linker-section contract.
    pub const fn new(name: &'static str, audit_surface_id: &'static str) -> Self {
        Self {
            name,
            audit_surface_id,
        }
    }

    /// Returns the retained linker section name.
    pub fn name(&self) -> &'static str {
        self.name
    }

    /// Returns the Phase 5 audit surface that owns this section.
    pub fn audit_surface_id(&self) -> &'static str {
        self.audit_surface_id
    }
}

/// Boot-mode-specific linker-script contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BootModeLinkerScript {
    retained_component_id: &'static str,
    bootloader_mode: BootloaderMode,
    active_script_path: &'static str,
    available_script_paths: &'static [&'static str],
    maybe_included_script_path: Option<&'static str>,
    sections: &'static [LinkerSection],
    evidence_classes: &'static [EvidenceClass],
    selection_note: &'static str,
}

impl BootModeLinkerScript {
    /// Creates a linker-script contract without mutating retained scripts.
    pub fn from_profile(profile: &ProductProfile) -> Self {
        match (profile.board(), profile.mcu(), profile.bootloader_mode()) {
            (BoardKind::XBuddyExtension, McuKind::Stm32H503CbU7, bootloader_mode) => Self {
                retained_component_id: "stm32h503-xbuddy-extension-startup-linker",
                bootloader_mode,
                active_script_path: "src/puppy/xbuddy_extension/stm32h503.ld",
                available_script_paths: STM32H503_XBUDDY_EXTENSION_LINKER_SCRIPTS,
                maybe_included_script_path: Some("src/puppy/xbuddy_extension/stm32h503.ld"),
                sections: H503_LINKER_SECTIONS,
                evidence_classes: LINKER_EVIDENCE_CLASSES,
                selection_note: "H503 xBuddy Extension keeps stm32h503_boot.ld and stm32h503_noboot.ld named while exact production Bazel platform/toolchain labels are deferred.",
            },
            (BoardKind::Dwarf | BoardKind::ModularBed, McuKind::Stm32G070RbT6, bootloader_mode)
            | (_, McuKind::Stm32G070RbT6, bootloader_mode) => Self {
                retained_component_id: "stm32g0-startup-linker",
                bootloader_mode,
                active_script_path: g0_active_script_path(bootloader_mode),
                available_script_paths: STM32G0_LINKER_SCRIPTS,
                maybe_included_script_path: None,
                sections: COMMON_LINKER_SECTIONS,
                evidence_classes: LINKER_EVIDENCE_CLASSES,
                selection_note: "G0 auxiliary linker evidence remains selected by retained CMake BOOT_SUFFIX behavior.",
            },
            (_, McuKind::Stm32F407Vg, bootloader_mode) => Self {
                retained_component_id: "stm32f4-startup-linker",
                bootloader_mode,
                active_script_path: f407_active_script_path(bootloader_mode),
                available_script_paths: STM32F407_LINKER_SCRIPTS,
                maybe_included_script_path: None,
                sections: COMMON_LINKER_SECTIONS,
                evidence_classes: LINKER_EVIDENCE_CLASSES,
                selection_note: "F407 linker evidence remains selected by retained CMake BOOT_SUFFIX behavior.",
            },
            (_, McuKind::Stm32F427Zi | McuKind::Stm32F429Vi, bootloader_mode) => Self {
                retained_component_id: "stm32f4-startup-linker",
                bootloader_mode,
                active_script_path: f42_active_script_path(bootloader_mode),
                available_script_paths: STM32F42_LINKER_SCRIPTS,
                maybe_included_script_path: None,
                sections: COMMON_LINKER_SECTIONS,
                evidence_classes: LINKER_EVIDENCE_CLASSES,
                selection_note: "F42x linker evidence remains selected by retained CMake BOOT_SUFFIX behavior.",
            },
            (_, McuKind::Stm32H503CbU7, bootloader_mode) => Self {
                retained_component_id: "stm32h503-xbuddy-extension-startup-linker",
                bootloader_mode,
                active_script_path: "src/puppy/xbuddy_extension/stm32h503.ld",
                available_script_paths: STM32H503_XBUDDY_EXTENSION_LINKER_SCRIPTS,
                maybe_included_script_path: Some("src/puppy/xbuddy_extension/stm32h503.ld"),
                sections: H503_LINKER_SECTIONS,
                evidence_classes: LINKER_EVIDENCE_CLASSES,
                selection_note: "H503 linker evidence is retained under xBuddy Extension until production platform labels are refined.",
            },
        }
    }

    /// Returns the retained foreign-code inventory row that owns this script.
    pub fn retained_component_id(&self) -> &'static str {
        self.retained_component_id
    }

    /// Returns the selected domain bootloader mode.
    pub fn bootloader_mode(&self) -> BootloaderMode {
        self.bootloader_mode
    }

    /// Returns the active or common retained linker script path for this contract.
    pub fn active_script_path(&self) -> &'static str {
        self.active_script_path
    }

    /// Returns all boot/noboot linker scripts that must remain visible.
    pub fn available_script_paths(&self) -> &'static [&'static str] {
        self.available_script_paths
    }

    /// Returns an included common linker script when boot/noboot wrappers include one.
    pub fn maybe_included_script_path(&self) -> Option<&'static str> {
        self.maybe_included_script_path
    }

    /// Returns retained linker sections that matter to runtime contracts.
    pub fn sections(&self) -> &'static [LinkerSection] {
        self.sections
    }

    /// Returns evidence classes for the linker contract.
    pub fn evidence_classes(&self) -> &'static [EvidenceClass] {
        self.evidence_classes
    }

    /// Returns the selection note that prevents hardware proof overclaiming.
    pub fn selection_note(&self) -> &'static str {
        self.selection_note
    }
}

fn f407_active_script_path(bootloader_mode: BootloaderMode) -> &'static str {
    match bootloader_mode {
        BootloaderMode::Boot => "src/device/stm32f4/linker/stm32f407vg_boot.ld",
        BootloaderMode::NoBoot | BootloaderMode::Auxiliary => {
            "src/device/stm32f4/linker/stm32f407vg.ld"
        }
    }
}

fn f42_active_script_path(bootloader_mode: BootloaderMode) -> &'static str {
    match bootloader_mode {
        BootloaderMode::Boot => "src/device/stm32f4/linker/stm32f42x_boot.ld",
        BootloaderMode::NoBoot | BootloaderMode::Auxiliary => {
            "src/device/stm32f4/linker/stm32f42x.ld"
        }
    }
}

fn g0_active_script_path(bootloader_mode: BootloaderMode) -> &'static str {
    match bootloader_mode {
        BootloaderMode::Boot | BootloaderMode::Auxiliary => {
            "src/device/stm32g0/linker/stm32g070rb_boot.ld"
        }
        BootloaderMode::NoBoot => "src/device/stm32g0/linker/stm32g070rb.ld",
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
    fn f4_boot_and_noboot_profiles_select_distinct_linker_scripts() {
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
        let boot_script = BootModeLinkerScript::from_profile(&boot_profile);
        let noboot_script = BootModeLinkerScript::from_profile(&noboot_profile);

        // Assert
        assert_eq!(
            boot_script.active_script_path(),
            "src/device/stm32f4/linker/stm32f407vg_boot.ld"
        );
        assert_eq!(
            noboot_script.active_script_path(),
            "src/device/stm32f4/linker/stm32f407vg.ld"
        );
        assert!(
            !boot_script
                .available_script_paths()
                .contains(&"src/puppy/xbuddy_extension/stm32h503_boot.ld")
        );
    }

    #[test]
    fn g0_auxiliary_profile_selects_g0_linker_evidence() {
        // Arrange
        let profile = profile(
            PrinterKind::Xl,
            BoardKind::Dwarf,
            McuKind::Stm32G070RbT6,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::Dwarf]),
        );

        // Act
        let linker_script = BootModeLinkerScript::from_profile(&profile);

        // Assert
        assert_eq!(
            linker_script.retained_component_id(),
            "stm32g0-startup-linker"
        );
        assert!(
            linker_script
                .available_script_paths()
                .contains(&"src/device/stm32g0/linker/stm32g070rb_boot.ld")
        );
    }

    #[test]
    fn h503_profile_names_boot_and_noboot_linker_scripts() {
        // Arrange
        let profile = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddyExtension,
            McuKind::Stm32H503CbU7,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::XBuddyExtension]),
        );

        // Act
        let linker_script = BootModeLinkerScript::from_profile(&profile);

        // Assert
        assert!(
            linker_script
                .available_script_paths()
                .contains(&"src/puppy/xbuddy_extension/stm32h503_boot.ld")
        );
        assert!(
            linker_script
                .available_script_paths()
                .contains(&"src/puppy/xbuddy_extension/stm32h503_noboot.ld")
        );
        assert_eq!(
            linker_script.maybe_included_script_path(),
            Some("src/puppy/xbuddy_extension/stm32h503.ld")
        );
        assert!(linker_script.selection_note().contains("deferred"));
    }

    #[test]
    fn linker_sections_keep_heap_vector_and_mutable_static_boundaries_named() {
        // Arrange
        let profile = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddyExtension,
            McuKind::Stm32H503CbU7,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::XBuddyExtension]),
        );

        // Act
        let linker_script = BootModeLinkerScript::from_profile(&profile);

        // Assert
        assert!(
            linker_script
                .sections()
                .iter()
                .any(|section| section.name() == ".isr_vector"
                    && section.audit_surface_id() == "startup-vector-contracts")
        );
        assert!(
            linker_script
                .sections()
                .iter()
                .any(|section| section.name() == "._user_heap_stack"
                    && section.audit_surface_id() == "allocator-heap-contracts")
        );
    }
}
