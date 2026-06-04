use std::collections::BTreeSet;

use crate::product::{BoardKind, PrinterKind, ProductProfile};

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

/// Phase 6 printing and safety feature gates derived from reference CMake facts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Phase6FeatureGate {
    /// Binary filament sensor path.
    HasFilamentSensorBinary,
    /// ADC filament sensor path.
    HasFilamentSensorAdc,
    /// Side filament sensor path.
    HasSideFilamentSensor,
    /// Trinamic motion driver support.
    HasTrinamic,
    /// TMC UART path.
    HasTmcUart,
    /// Cartesian precise homing.
    HasPreciseHoming,
    /// CoreXY precise homing.
    HasPreciseHomingCorexy,
    /// Input shaper calibration.
    HasInputShaperCalibration,
    /// Phase stepping.
    HasPhaseStepping,
    /// Phase stepping calibration.
    HasPhaseSteppingCalibration,
    /// Burst stepping when explicitly enabled.
    HasBurstStepping,
    /// Loadcell gate.
    HasLoadcell,
    /// HX717 loadcell gate.
    HasLoadcellHx717,
    /// Local bed controlled by the master board.
    HasLocalBed,
    /// Modular bed gate.
    HasModularBed,
    /// Remote bed gate.
    HasRemoteBed,
    /// Chamber API gate.
    HasChamberApi,
    /// Chamber filtration API gate.
    HasChamberFiltrationApi,
    /// Door sensor gate.
    HasDoorSensor,
    /// MMU2 gate fact.
    HasMmu2,
    /// NFC gate fact.
    HasNfc,
    /// LED gate fact.
    HasLeds,
    /// Side LED gate fact.
    HasSideLeds,
    /// Toolchanger gate fact.
    HasToolchanger,
    /// xBuddy Extension gate fact.
    HasXBuddyExtension,
    /// Serial print gate fact.
    HasSerialPrint,
    /// Emergency stop gate fact.
    HasEmergencyStop,
}

/// Phase 6 gate availability state.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum GateState {
    /// The gate is enabled for this validated profile.
    Enabled,
    /// The gate is disabled for this validated profile.
    Disabled,
    /// Auxiliary runtime behavior remains Phase 10 scope.
    OutOfScopePhase10,
}

/// Explicit build-mode input for burst stepping.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum BurstSteppingMode {
    /// Burst stepping is explicitly enabled.
    Enabled,
    /// Burst stepping is disabled.
    Disabled,
}

/// Phase 6 feature-gate facts keyed by a validated product profile.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Phase6FeatureGates {
    printer: PrinterKind,
    board: BoardKind,
    is_auxiliary: bool,
    burst_stepping_mode: BurstSteppingMode,
}

impl Phase6FeatureGates {
    /// Derives Phase 6 feature-gate facts from a validated product profile.
    pub fn from_profile(profile: &ProductProfile, burst_stepping_mode: BurstSteppingMode) -> Self {
        Self {
            printer: profile.printer(),
            board: profile.board(),
            is_auxiliary: profile.is_auxiliary(),
            burst_stepping_mode,
        }
    }

    /// Returns the availability state for one Phase 6 feature gate.
    pub fn gate_state(&self, gate: Phase6FeatureGate) -> GateState {
        if self.is_auxiliary {
            return self.auxiliary_gate_state(gate);
        }

        if self.master_gate_enabled(gate) {
            GateState::Enabled
        } else {
            GateState::Disabled
        }
    }

    fn auxiliary_gate_state(&self, gate: Phase6FeatureGate) -> GateState {
        match (self.board, gate) {
            (BoardKind::Dwarf, Phase6FeatureGate::HasLoadcellHx717)
            | (BoardKind::XBuddyExtension, Phase6FeatureGate::HasXBuddyExtension) => {
                GateState::Enabled
            }
            _ => GateState::OutOfScopePhase10,
        }
    }

    fn master_gate_enabled(&self, gate: Phase6FeatureGate) -> bool {
        match gate {
            Phase6FeatureGate::HasFilamentSensorBinary => {
                matches!(self.printer, PrinterKind::Mini | PrinterKind::Mk35)
            }
            Phase6FeatureGate::HasFilamentSensorAdc => matches!(
                self.printer,
                PrinterKind::Mk4
                    | PrinterKind::Xl
                    | PrinterKind::Ix
                    | PrinterKind::XlDevKit
                    | PrinterKind::CoreOne
            ),
            Phase6FeatureGate::HasSideFilamentSensor => {
                matches!(
                    self.printer,
                    PrinterKind::Ix | PrinterKind::Xl | PrinterKind::CoreOne
                )
            }
            Phase6FeatureGate::HasTrinamic => matches!(
                self.printer,
                PrinterKind::Mini
                    | PrinterKind::Mk4
                    | PrinterKind::Mk35
                    | PrinterKind::Ix
                    | PrinterKind::Xl
                    | PrinterKind::XlDevKit
                    | PrinterKind::CoreOne
            ),
            Phase6FeatureGate::HasTmcUart => matches!(self.printer, PrinterKind::Mini),
            Phase6FeatureGate::HasPreciseHoming => {
                matches!(self.printer, PrinterKind::Mk4 | PrinterKind::Mk35)
            }
            Phase6FeatureGate::HasPreciseHomingCorexy => matches!(
                self.printer,
                PrinterKind::Ix | PrinterKind::Xl | PrinterKind::XlDevKit | PrinterKind::CoreOne
            ),
            Phase6FeatureGate::HasInputShaperCalibration => matches!(
                self.printer,
                PrinterKind::Mk4
                    | PrinterKind::Mk35
                    | PrinterKind::Xl
                    | PrinterKind::XlDevKit
                    | PrinterKind::CoreOne
            ),
            Phase6FeatureGate::HasPhaseStepping
            | Phase6FeatureGate::HasPhaseSteppingCalibration => {
                matches!(
                    self.printer,
                    PrinterKind::Xl | PrinterKind::Ix | PrinterKind::CoreOne
                )
            }
            Phase6FeatureGate::HasBurstStepping => {
                matches!(self.burst_stepping_mode, BurstSteppingMode::Enabled)
                    && matches!(
                        self.printer,
                        PrinterKind::Xl | PrinterKind::Mk4 | PrinterKind::Ix | PrinterKind::CoreOne
                    )
            }
            Phase6FeatureGate::HasLoadcell => matches!(
                self.printer,
                PrinterKind::Mk4
                    | PrinterKind::Ix
                    | PrinterKind::Xl
                    | PrinterKind::XlDevKit
                    | PrinterKind::CoreOne
            ),
            Phase6FeatureGate::HasLoadcellHx717 => {
                matches!(self.board, BoardKind::XBuddy)
                    && !matches!(self.printer, PrinterKind::Mk35)
            }
            Phase6FeatureGate::HasLocalBed => matches!(
                self.printer,
                PrinterKind::CoreOne | PrinterKind::Mini | PrinterKind::Mk4 | PrinterKind::Mk35
            ),
            Phase6FeatureGate::HasModularBed | Phase6FeatureGate::HasRemoteBed => {
                matches!(
                    self.printer,
                    PrinterKind::Ix | PrinterKind::Xl | PrinterKind::XlDevKit
                )
            }
            Phase6FeatureGate::HasChamberApi | Phase6FeatureGate::HasChamberFiltrationApi => {
                matches!(self.printer, PrinterKind::Xl | PrinterKind::CoreOne)
            }
            Phase6FeatureGate::HasDoorSensor => {
                matches!(self.printer, PrinterKind::CoreOne | PrinterKind::Mk4)
            }
            Phase6FeatureGate::HasMmu2 => matches!(
                self.printer,
                PrinterKind::Mk4 | PrinterKind::Mk35 | PrinterKind::CoreOne
            ),
            Phase6FeatureGate::HasNfc => matches!(
                self.printer,
                PrinterKind::Mk35 | PrinterKind::Mk4 | PrinterKind::CoreOne
            ),
            Phase6FeatureGate::HasLeds => matches!(
                self.printer,
                PrinterKind::Mk4
                    | PrinterKind::Mk35
                    | PrinterKind::Xl
                    | PrinterKind::Ix
                    | PrinterKind::CoreOne
            ),
            Phase6FeatureGate::HasSideLeds => {
                matches!(
                    self.printer,
                    PrinterKind::Xl | PrinterKind::Ix | PrinterKind::CoreOne
                )
            }
            Phase6FeatureGate::HasToolchanger => {
                matches!(self.printer, PrinterKind::Xl | PrinterKind::XlDevKit)
            }
            Phase6FeatureGate::HasXBuddyExtension => matches!(self.printer, PrinterKind::CoreOne),
            Phase6FeatureGate::HasSerialPrint => matches!(
                self.printer,
                PrinterKind::Mk4
                    | PrinterKind::Mk35
                    | PrinterKind::Xl
                    | PrinterKind::Ix
                    | PrinterKind::Mini
                    | PrinterKind::CoreOne
            ),
            Phase6FeatureGate::HasEmergencyStop => matches!(self.printer, PrinterKind::CoreOne),
        }
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
