use std::collections::BTreeSet;

/// Firmware feature flags that affect product-specific behavior.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Feature {
    /// Local PrusaLink/WUI server.
    WebUi,
    /// Prusa Connect client.
    Connect,
    /// External resource package support.
    Resources,
    /// Compiled translation assets.
    Translations,
    /// Touch UI feature surface.
    Touch,
    /// MMU2 runtime integration.
    Mmu2,
    /// XL/iX/CORE One auxiliary-controller ecosystem.
    Puppies,
    /// Dwarf toolhead auxiliary firmware.
    Dwarf,
    /// Modular bed auxiliary firmware.
    ModularBed,
    /// CORE One xBuddy Extension firmware.
    XBuddyExtension,
    /// USB device support.
    UsbDevice,
    /// NFC feature surface.
    Nfc,
}

/// De-duplicated feature set for a firmware profile.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct FeatureSet {
    features: BTreeSet<Feature>,
}

impl FeatureSet {
    /// Creates an empty feature set.
    pub fn empty() -> Self {
        Self::default()
    }

    /// Creates a de-duplicated feature set from raw feature flags.
    pub fn from_features(features: impl IntoIterator<Item = Feature>) -> Self {
        Self {
            features: features.into_iter().collect(),
        }
    }

    /// Returns true when the feature is present.
    pub fn contains(&self, feature: Feature) -> bool {
        self.features.contains(&feature)
    }

    /// Iterates over features in deterministic order.
    pub fn iter(&self) -> impl Iterator<Item = Feature> + '_ {
        self.features.iter().copied()
    }
}

#[cfg(test)]
mod phase6_tests {
    use super::*;
    use crate::{BoardKind, BootloaderMode, McuKind, PrinterKind, ProductProfile};

    fn profile(
        printer: PrinterKind,
        board: BoardKind,
        mcu: McuKind,
        bootloader_mode: BootloaderMode,
        features: FeatureSet,
    ) -> ProductProfile {
        ProductProfile::new(printer, board, mcu, bootloader_mode, features)
            .expect("test profile is part of the supported reference matrix")
    }

    #[test]
    fn coreone_xbuddy_master_enables_printing_safety_gate_facts() {
        // Arrange
        let profile = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddy,
            McuKind::Stm32F427Zi,
            BootloaderMode::Boot,
            FeatureSet::from_features([
                Feature::Mmu2,
                Feature::Nfc,
                Feature::Puppies,
                Feature::XBuddyExtension,
            ]),
        );

        // Act
        let gates = Phase6FeatureGates::from_profile(&profile, BurstSteppingMode::Disabled);

        // Assert
        for gate in [
            Phase6FeatureGate::HasXBuddyExtension,
            Phase6FeatureGate::HasDoorSensor,
            Phase6FeatureGate::HasChamberApi,
            Phase6FeatureGate::HasNfc,
            Phase6FeatureGate::HasMmu2,
            Phase6FeatureGate::HasLeds,
            Phase6FeatureGate::HasEmergencyStop,
        ] {
            assert_eq!(gates.gate_state(gate), GateState::Enabled);
        }
    }

    #[test]
    fn mini_buddy_master_enables_local_print_gate_facts_without_mmu2() {
        // Arrange
        let profile = profile(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );

        // Act
        let gates = Phase6FeatureGates::from_profile(&profile, BurstSteppingMode::Disabled);

        // Assert
        for gate in [
            Phase6FeatureGate::HasFilamentSensorBinary,
            Phase6FeatureGate::HasTmcUart,
            Phase6FeatureGate::HasLocalBed,
            Phase6FeatureGate::HasSerialPrint,
        ] {
            assert_eq!(gates.gate_state(gate), GateState::Enabled);
        }
        assert_eq!(
            gates.gate_state(Phase6FeatureGate::HasMmu2),
            GateState::Disabled
        );
    }

    #[test]
    fn xl_xlbuddy_master_enables_toolchanger_and_remote_motion_gate_facts_without_nfc() {
        // Arrange
        let profile = profile(
            PrinterKind::Xl,
            BoardKind::XlBuddy,
            McuKind::Stm32F427Zi,
            BootloaderMode::Boot,
            FeatureSet::from_features([Feature::Puppies, Feature::Dwarf, Feature::ModularBed]),
        );

        // Act
        let gates = Phase6FeatureGates::from_profile(&profile, BurstSteppingMode::Disabled);

        // Assert
        for gate in [
            Phase6FeatureGate::HasToolchanger,
            Phase6FeatureGate::HasModularBed,
            Phase6FeatureGate::HasRemoteBed,
            Phase6FeatureGate::HasPhaseStepping,
            Phase6FeatureGate::HasLoadcell,
            Phase6FeatureGate::HasChamberApi,
        ] {
            assert_eq!(gates.gate_state(gate), GateState::Enabled);
        }
        assert_eq!(
            gates.gate_state(Phase6FeatureGate::HasNfc),
            GateState::Disabled
        );
    }

    #[test]
    fn xbuddy_extension_auxiliary_keeps_runtime_behavior_out_of_phase6_scope() {
        // Arrange
        let profile = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddyExtension,
            McuKind::Stm32H503CbU7,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::XBuddyExtension]),
        );

        // Act
        let gates = Phase6FeatureGates::from_profile(&profile, BurstSteppingMode::Disabled);

        // Assert
        assert_eq!(
            gates.gate_state(Phase6FeatureGate::HasXBuddyExtension),
            GateState::Enabled
        );
        assert_eq!(
            gates.gate_state(Phase6FeatureGate::HasToolchanger),
            GateState::OutOfScopePhase10
        );
        assert_eq!(
            gates.gate_state(Phase6FeatureGate::HasMmu2),
            GateState::OutOfScopePhase10
        );
    }

    #[test]
    fn burst_stepping_requires_supported_master_printer_and_explicit_enablement() {
        // Arrange
        let coreone = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddy,
            McuKind::Stm32F427Zi,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );
        let mini = profile(
            PrinterKind::Mini,
            BoardKind::Buddy,
            McuKind::Stm32F407Vg,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );
        let xbuddy_extension = profile(
            PrinterKind::CoreOne,
            BoardKind::XBuddyExtension,
            McuKind::Stm32H503CbU7,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::XBuddyExtension]),
        );

        // Act
        let enabled_coreone =
            Phase6FeatureGates::from_profile(&coreone, BurstSteppingMode::Enabled);
        let disabled_coreone =
            Phase6FeatureGates::from_profile(&coreone, BurstSteppingMode::Disabled);
        let enabled_mini = Phase6FeatureGates::from_profile(&mini, BurstSteppingMode::Enabled);
        let enabled_auxiliary =
            Phase6FeatureGates::from_profile(&xbuddy_extension, BurstSteppingMode::Enabled);

        // Assert
        assert_eq!(
            enabled_coreone.gate_state(Phase6FeatureGate::HasBurstStepping),
            GateState::Enabled
        );
        assert_eq!(
            disabled_coreone.gate_state(Phase6FeatureGate::HasBurstStepping),
            GateState::Disabled
        );
        assert_eq!(
            enabled_mini.gate_state(Phase6FeatureGate::HasBurstStepping),
            GateState::Disabled
        );
        assert_eq!(
            enabled_auxiliary.gate_state(Phase6FeatureGate::HasBurstStepping),
            GateState::OutOfScopePhase10
        );
    }

    #[test]
    fn hx717_loadcell_gate_follows_reference_board_and_mk35_exception() {
        // Arrange
        let dwarf = profile(
            PrinterKind::Xl,
            BoardKind::Dwarf,
            McuKind::Stm32G070RbT6,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::Dwarf]),
        );
        let mk4_xbuddy = profile(
            PrinterKind::Mk4,
            BoardKind::XBuddy,
            McuKind::Stm32F427Zi,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );
        let mk35_xbuddy = profile(
            PrinterKind::Mk35,
            BoardKind::XBuddy,
            McuKind::Stm32F427Zi,
            BootloaderMode::Boot,
            FeatureSet::empty(),
        );

        // Act
        let dwarf_gates = Phase6FeatureGates::from_profile(&dwarf, BurstSteppingMode::Disabled);
        let mk4_gates = Phase6FeatureGates::from_profile(&mk4_xbuddy, BurstSteppingMode::Disabled);
        let mk35_gates =
            Phase6FeatureGates::from_profile(&mk35_xbuddy, BurstSteppingMode::Disabled);

        // Assert
        assert_eq!(
            dwarf_gates.gate_state(Phase6FeatureGate::HasLoadcellHx717),
            GateState::Enabled
        );
        assert_eq!(
            mk4_gates.gate_state(Phase6FeatureGate::HasLoadcellHx717),
            GateState::Enabled
        );
        assert_eq!(
            mk35_gates.gate_state(Phase6FeatureGate::HasLoadcellHx717),
            GateState::Disabled
        );
    }
}
