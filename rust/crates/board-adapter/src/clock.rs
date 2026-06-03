use crate::{BoardRuntimeSurface, McuFamily};
use buddy_domain::ProductProfile;

const STM32F4_CLOCK_PATHS: &[&str] = &[
    "src/device/stm32f4/core_init.cpp",
    "src/device/stm32f4/cmsis.cpp",
];
const STM32G0_CLOCK_PATHS: &[&str] = &[
    "src/device/stm32g0/core_init.cpp",
    "src/device/stm32g0/cmsis.cpp",
];
const STM32H503_XBUDDY_EXTENSION_CLOCK_PATHS: &[&str] = &[
    "src/puppy/xbuddy_extension/cmsis.cpp",
    "src/puppy/xbuddy_extension/hal_clock.cpp",
];
const SHARED_CLOCK_EVIDENCE_NOTES: &[&str] = &[
    "HSE_VALUE",
    "SystemCoreClock",
    "SYSTEM_CORE_CLOCK",
    "configCPU_CLOCK_HZ",
    "clock hardware behavior remains manual-hardware-required",
];
const STM32H503_XBUDDY_EXTENSION_EVIDENCE_NOTES: &[&str] = &[
    "HSE_VALUE",
    "SystemCoreClock",
    "configCPU_CLOCK_HZ",
    "fpv5-sp-d16",
    "clock hardware behavior remains manual-hardware-required",
];

/// Board clock source expected by a retained runtime clock tree.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ClockSource {
    /// External crystal oscillator selected as HSE/PLL input.
    ExternalCrystal,
}

/// Expected core clock frequency in hertz.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct CoreClockHz(u32);

impl CoreClockHz {
    /// Creates a typed core-clock value.
    pub const fn new(hz: u32) -> Self {
        Self(hz)
    }

    /// Returns the raw hertz value.
    pub fn get(self) -> u32 {
        self.0
    }
}

/// Typed board clock-tree contract derived from a validated product profile.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BoardClockTree {
    mcu_family: McuFamily,
    clock_source: ClockSource,
    core_clock_hz: CoreClockHz,
    source_evidence_paths: &'static [&'static str],
    evidence_notes: &'static [&'static str],
}

impl BoardClockTree {
    /// Creates a board clock-tree contract without mutating hardware clocks.
    pub fn from_profile(profile: &ProductProfile) -> Self {
        let surface = BoardRuntimeSurface::from_profile(profile);

        match surface.mcu_family() {
            McuFamily::Stm32F4 => Self {
                mcu_family: McuFamily::Stm32F4,
                clock_source: ClockSource::ExternalCrystal,
                core_clock_hz: CoreClockHz::new(168_000_000),
                source_evidence_paths: STM32F4_CLOCK_PATHS,
                evidence_notes: SHARED_CLOCK_EVIDENCE_NOTES,
            },
            McuFamily::Stm32G0 => Self {
                mcu_family: McuFamily::Stm32G0,
                clock_source: ClockSource::ExternalCrystal,
                core_clock_hz: CoreClockHz::new(56_000_000),
                source_evidence_paths: STM32G0_CLOCK_PATHS,
                evidence_notes: SHARED_CLOCK_EVIDENCE_NOTES,
            },
            McuFamily::Stm32H503XbuddyExtension => Self {
                mcu_family: McuFamily::Stm32H503XbuddyExtension,
                clock_source: ClockSource::ExternalCrystal,
                core_clock_hz: CoreClockHz::new(240_000_000),
                source_evidence_paths: STM32H503_XBUDDY_EXTENSION_CLOCK_PATHS,
                evidence_notes: STM32H503_XBUDDY_EXTENSION_EVIDENCE_NOTES,
            },
        }
    }

    /// Returns the MCU runtime family for this clock contract.
    pub fn mcu_family(&self) -> McuFamily {
        self.mcu_family
    }

    /// Returns the retained clock source.
    pub fn clock_source(&self) -> ClockSource {
        self.clock_source
    }

    /// Returns the expected retained core-clock value.
    pub fn core_clock_hz(&self) -> CoreClockHz {
        self.core_clock_hz
    }

    /// Returns source files that provide evidence for this clock tree.
    pub fn source_evidence_paths(&self) -> &'static [&'static str] {
        self.source_evidence_paths
    }

    /// Returns non-local evidence notes that keep hardware proof explicit.
    pub fn evidence_notes(&self) -> &'static [&'static str] {
        self.evidence_notes
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
    fn maps_board_clock_tree_to_family_specific_source_evidence() {
        // Arrange
        let f4_profile = profile(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );
        let g0_profile = profile(
            PrinterKind::Xl,
            BoardKind::Dwarf,
            McuKind::Stm32G070RbT6,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::Dwarf]),
        );
        let h503_profile = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddyExtension,
            McuKind::Stm32H503CbU7,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::XBuddyExtension]),
        );

        // Act
        let f4_tree = BoardClockTree::from_profile(&f4_profile);
        let g0_tree = BoardClockTree::from_profile(&g0_profile);
        let h503_tree = BoardClockTree::from_profile(&h503_profile);

        // Assert
        assert!(
            f4_tree
                .source_evidence_paths()
                .contains(&"src/device/stm32f4/core_init.cpp")
        );
        assert!(
            f4_tree
                .source_evidence_paths()
                .contains(&"src/device/stm32f4/cmsis.cpp")
        );
        assert!(
            g0_tree
                .source_evidence_paths()
                .contains(&"src/device/stm32g0/core_init.cpp")
        );
        assert!(
            g0_tree
                .source_evidence_paths()
                .contains(&"src/device/stm32g0/cmsis.cpp")
        );
        assert!(
            h503_tree
                .source_evidence_paths()
                .contains(&"src/puppy/xbuddy_extension/cmsis.cpp")
        );
        assert!(
            h503_tree
                .source_evidence_paths()
                .contains(&"src/puppy/xbuddy_extension/hal_clock.cpp")
        );
        assert!(h503_tree.evidence_notes().contains(&"configCPU_CLOCK_HZ"));
        assert_eq!(f4_tree.clock_source(), ClockSource::ExternalCrystal);
        assert_eq!(g0_tree.clock_source(), ClockSource::ExternalCrystal);
        assert_eq!(h503_tree.core_clock_hz(), CoreClockHz::new(240_000_000));
    }
}
