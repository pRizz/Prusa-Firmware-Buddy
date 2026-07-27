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
    /// ADC side filament sensor path.
    HasAdcSideFilamentSensor,
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
    /// MMU2 transport over the xBuddy UART rather than puppy Modbus.
    HasMmu2OverUart,
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
            Phase6FeatureGate::HasAdcSideFilamentSensor => matches!(self.printer, PrinterKind::Xl),
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
            Phase6FeatureGate::HasMmu2OverUart => {
                matches!(self.board, BoardKind::XBuddy)
                    && matches!(self.printer, PrinterKind::Mk4 | PrinterKind::Mk35)
            }
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
mod tests;
