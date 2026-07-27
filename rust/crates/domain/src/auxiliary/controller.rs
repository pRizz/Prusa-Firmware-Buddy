use super::identity::{AuxiliaryControllerKind, is_valid_auxiliary_row_id};
use super::transport::{AuxiliaryProofScope, BusEvidenceClass};
use crate::{BoardKind, Feature, InvariantError, ProductProfile};

/// Dock identity for toolchanger and expansion ecosystem contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum DockIdentity {
    /// Modular Bed identity.
    ModularBed,
    /// Dwarf dock 1 identity.
    Dwarf1,
    /// Dwarf dock 2 identity.
    Dwarf2,
    /// Dwarf dock 3 identity.
    Dwarf3,
    /// Dwarf dock 4 identity.
    Dwarf4,
    /// Dwarf dock 5 identity.
    Dwarf5,
    /// Dwarf dock 6 identity.
    Dwarf6,
    /// xBuddy Extension identity.
    XBuddyExtension,
}

impl DockIdentity {
    /// Parses a dock identity string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "MODULAR_BED" => Ok(Self::ModularBed),
            "DWARF_1" => Ok(Self::Dwarf1),
            "DWARF_2" => Ok(Self::Dwarf2),
            "DWARF_3" => Ok(Self::Dwarf3),
            "DWARF_4" => Ok(Self::Dwarf4),
            "DWARF_5" => Ok(Self::Dwarf5),
            "DWARF_6" => Ok(Self::Dwarf6),
            "XBUDDY_EXTENSION" => Ok(Self::XBuddyExtension),
            _ => Err(InvariantError::InvalidDockIdentity),
        }
    }

    /// Returns the manifest string for this dock identity.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::ModularBed => "MODULAR_BED",
            Self::Dwarf1 => "DWARF_1",
            Self::Dwarf2 => "DWARF_2",
            Self::Dwarf3 => "DWARF_3",
            Self::Dwarf4 => "DWARF_4",
            Self::Dwarf5 => "DWARF_5",
            Self::Dwarf6 => "DWARF_6",
            Self::XBuddyExtension => "XBUDDY_EXTENSION",
        }
    }
}

/// Tool-offset axis represented by Phase 10 contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ToolOffsetAxis {
    /// X offset axis.
    X,
    /// Y offset axis.
    Y,
    /// Z offset axis.
    Z,
}

/// Tool-offset identity limited to retained tool numbers.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ToolOffsetIdentity {
    tool_number: u8,
    axis: ToolOffsetAxis,
}

impl ToolOffsetIdentity {
    /// Creates a tool-offset identity for tool numbers 1 through 6.
    pub fn new(tool_number: u8, axis: ToolOffsetAxis) -> Result<Self, InvariantError> {
        if !(1..=6).contains(&tool_number) {
            return Err(InvariantError::InvalidToolOffsetIdentity);
        }

        Ok(Self { tool_number, axis })
    }

    /// Returns the validated tool number.
    pub fn tool_number(self) -> u8 {
        self.tool_number
    }

    /// Returns the offset axis.
    pub fn axis(self) -> ToolOffsetAxis {
        self.axis
    }
}

/// Auxiliary controller fault classification.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ControllerFaultClass {
    /// No fault is present.
    NoFault,
    /// Bootloader is incompatible.
    BootloaderIncompatible,
    /// Firmware fingerprint mismatch.
    FingerprintMismatch,
    /// Controller discovery failed.
    DiscoverError,
    /// Flash write failed.
    FlashWriteError,
    /// Modbus communication failed.
    ModbusCommunication,
    /// Dwarf TMC fault.
    DwarfTmc,
    /// Dwarf Marlin killed state.
    DwarfMarlinKilled,
    /// Modular Bed fault.
    ModularBedFault,
    /// Modular Bed panic.
    ModularBedPanic,
    /// xBuddy Extension MMU bridge fault.
    XBuddyExtensionMmuBridge,
    /// Unknown retained fault class.
    Unknown,
}

impl ControllerFaultClass {
    /// Parses an auxiliary controller fault class string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "no-fault" => Ok(Self::NoFault),
            "bootloader-incompatible" => Ok(Self::BootloaderIncompatible),
            "fingerprint-mismatch" => Ok(Self::FingerprintMismatch),
            "discover-error" => Ok(Self::DiscoverError),
            "flash-write-error" => Ok(Self::FlashWriteError),
            "modbus-communication" => Ok(Self::ModbusCommunication),
            "dwarf-tmc" => Ok(Self::DwarfTmc),
            "dwarf-marlin-killed" => Ok(Self::DwarfMarlinKilled),
            "modular-bed-fault" => Ok(Self::ModularBedFault),
            "modular-bed-panic" => Ok(Self::ModularBedPanic),
            "xbuddy-extension-mmu-bridge" => Ok(Self::XBuddyExtensionMmuBridge),
            "unknown" => Ok(Self::Unknown),
            _ => Err(InvariantError::InvalidControllerFaultClass),
        }
    }

    /// Returns the manifest string for this fault class.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::NoFault => "no-fault",
            Self::BootloaderIncompatible => "bootloader-incompatible",
            Self::FingerprintMismatch => "fingerprint-mismatch",
            Self::DiscoverError => "discover-error",
            Self::FlashWriteError => "flash-write-error",
            Self::ModbusCommunication => "modbus-communication",
            Self::DwarfTmc => "dwarf-tmc",
            Self::DwarfMarlinKilled => "dwarf-marlin-killed",
            Self::ModularBedFault => "modular-bed-fault",
            Self::ModularBedPanic => "modular-bed-panic",
            Self::XBuddyExtensionMmuBridge => "xbuddy-extension-mmu-bridge",
            Self::Unknown => "unknown",
        }
    }
}

/// Phase 10 auxiliary parity row identity.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct AuxiliaryParityRowId(String);

impl AuxiliaryParityRowId {
    /// Parses a path-free printable ASCII auxiliary parity row ID.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(InvariantError::EmptyAuxiliaryParityRowId);
        }

        if !is_valid_auxiliary_row_id(&raw) {
            return Err(InvariantError::InvalidAuxiliaryParityRowId);
        }

        Ok(Self(raw))
    }

    /// Returns the validated row ID as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Raw inputs for creating an [`AuxiliaryParityContract`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuxiliaryParityContractInput {
    /// Phase 10 row identity.
    pub row_id: AuxiliaryParityRowId,
    /// Evidence class for this row.
    pub evidence_class: BusEvidenceClass,
    /// Proof scope for this row.
    pub proof_scope: AuxiliaryProofScope,
}

/// Validated Phase 10 auxiliary parity row contract.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuxiliaryParityContract {
    row_id: AuxiliaryParityRowId,
    evidence_class: BusEvidenceClass,
    proof_scope: AuxiliaryProofScope,
}

impl AuxiliaryParityContract {
    /// Creates a parity contract when evidence/proof compatibility is valid.
    pub fn new(input: AuxiliaryParityContractInput) -> Result<Self, InvariantError> {
        let AuxiliaryParityContractInput {
            row_id,
            evidence_class,
            proof_scope,
        } = input;

        if matches!(proof_scope, AuxiliaryProofScope::Local) && !evidence_class.is_local_proof() {
            return Err(InvariantError::InvalidAuxiliaryParityContract);
        }

        Ok(Self {
            row_id,
            evidence_class,
            proof_scope,
        })
    }

    /// Returns the row ID.
    pub fn row_id(&self) -> &AuxiliaryParityRowId {
        &self.row_id
    }

    /// Returns the evidence class.
    pub fn evidence_class(&self) -> BusEvidenceClass {
        self.evidence_class
    }

    /// Returns the proof scope.
    pub fn proof_scope(&self) -> AuxiliaryProofScope {
        self.proof_scope
    }
}

/// Raw inputs for creating an [`AuxiliaryControllerContract`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuxiliaryControllerContractInput {
    /// Validated product profile that owns this controller contract.
    pub profile: ProductProfile,
    /// Auxiliary controller kind to expose for this profile.
    pub controller_kind: AuxiliaryControllerKind,
}

/// Product/profile-gated auxiliary controller contract.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuxiliaryControllerContract {
    profile: ProductProfile,
    controller_kind: AuxiliaryControllerKind,
}

impl AuxiliaryControllerContract {
    /// Creates a controller contract only for supported profile/controller pairs.
    pub fn new(input: AuxiliaryControllerContractInput) -> Result<Self, InvariantError> {
        let AuxiliaryControllerContractInput {
            profile,
            controller_kind,
        } = input;

        let supported = match (profile.board(), controller_kind) {
            (BoardKind::Dwarf, AuxiliaryControllerKind::Dwarf)
            | (BoardKind::ModularBed, AuxiliaryControllerKind::ModularBed)
            | (BoardKind::XBuddyExtension, AuxiliaryControllerKind::XBuddyExtension) => true,
            (_, AuxiliaryControllerKind::Mmu2) => {
                !profile.is_auxiliary() && profile.features().contains(Feature::Mmu2)
            }
            _ => false,
        };

        if !supported {
            return Err(InvariantError::UnsupportedAuxiliaryController);
        }

        Ok(Self {
            profile,
            controller_kind,
        })
    }

    /// Returns the validated product profile.
    pub fn profile(&self) -> &ProductProfile {
        &self.profile
    }

    /// Returns the auxiliary controller kind.
    pub fn controller_kind(&self) -> AuxiliaryControllerKind {
        self.controller_kind
    }
}
