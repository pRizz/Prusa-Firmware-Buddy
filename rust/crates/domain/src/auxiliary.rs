use crate::{BoardKind, Feature, InvariantError, ProductProfile};

fn is_valid_auxiliary_row_id(raw: &str) -> bool {
    raw != "."
        && raw != ".."
        && raw.len() <= 96
        && !raw.contains('/')
        && !raw.contains('\\')
        && raw.bytes().all(|byte| byte.is_ascii_graphic())
}

/// Auxiliary controller family represented by Phase 10 parity contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum AuxiliaryControllerKind {
    /// Dwarf toolhead auxiliary controller.
    Dwarf,
    /// Modular Bed auxiliary controller.
    ModularBed,
    /// xBuddy Extension auxiliary controller.
    XBuddyExtension,
    /// MMU2 controller or transport integration.
    Mmu2,
}

impl AuxiliaryControllerKind {
    /// Parses an auxiliary controller kind string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "dwarf" => Ok(Self::Dwarf),
            "modular-bed" => Ok(Self::ModularBed),
            "xbuddy-extension" => Ok(Self::XBuddyExtension),
            "mmu2" => Ok(Self::Mmu2),
            _ => Err(InvariantError::InvalidAuxiliaryControllerKind),
        }
    }

    /// Returns the manifest string for this controller kind.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Dwarf => "dwarf",
            Self::ModularBed => "modular-bed",
            Self::XBuddyExtension => "xbuddy-extension",
            Self::Mmu2 => "mmu2",
        }
    }
}

/// Auxiliary-controller runtime state visible to compatibility contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum AuxiliaryRuntimeState {
    /// Controller is in bootloader mode.
    Bootloader,
    /// Controller is unavailable.
    Unavailable,
    /// Controller is active.
    Active,
    /// Controller is stopped.
    Stopped,
    /// Controller is updating.
    Updating,
    /// Controller update failed.
    UpdateFailed,
    /// Controller communication fault is present.
    CommunicationFault,
    /// Reference behavior is unknown and explicitly deferred.
    UnknownReferenceDeferred,
}

impl AuxiliaryRuntimeState {
    /// Parses an auxiliary runtime state string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "bootloader" => Ok(Self::Bootloader),
            "unavailable" => Ok(Self::Unavailable),
            "active" => Ok(Self::Active),
            "stopped" => Ok(Self::Stopped),
            "updating" => Ok(Self::Updating),
            "update-failed" => Ok(Self::UpdateFailed),
            "communication-fault" => Ok(Self::CommunicationFault),
            "unknown-reference-deferred" => Ok(Self::UnknownReferenceDeferred),
            _ => Err(InvariantError::InvalidAuxiliaryRuntimeState),
        }
    }

    /// Returns the manifest string for this runtime state.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Bootloader => "bootloader",
            Self::Unavailable => "unavailable",
            Self::Active => "active",
            Self::Stopped => "stopped",
            Self::Updating => "updating",
            Self::UpdateFailed => "update-failed",
            Self::CommunicationFault => "communication-fault",
            Self::UnknownReferenceDeferred => "unknown-reference-deferred",
        }
    }
}

/// Named firmware image source without firmware payload bytes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum FirmwareImageSource {
    /// Dwarf firmware prebuilt path CMake variable.
    DwarfBinaryPath,
    /// Modular Bed firmware prebuilt path CMake variable.
    ModularBedBinaryPath,
    /// xBuddy Extension firmware prebuilt path CMake variable.
    XBuddyExtensionBinaryPath,
    /// Dwarf firmware runtime resource path.
    DwarfResourcePath,
    /// Modular Bed firmware runtime resource path.
    ModularBedResourcePath,
    /// xBuddy Extension firmware runtime resource path.
    XBuddyExtensionResourcePath,
    /// MMU firmware runtime resource path.
    MmuFirmwareResourcePath,
}

impl FirmwareImageSource {
    /// Parses a named firmware image source string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "DWARF_BINARY_PATH" => Ok(Self::DwarfBinaryPath),
            "MODULARBED_BINARY_PATH" => Ok(Self::ModularBedBinaryPath),
            "XBUDDY_EXTENSION_BINARY_PATH" => Ok(Self::XBuddyExtensionBinaryPath),
            "/puppies/fw-dwarf.bin" => Ok(Self::DwarfResourcePath),
            "/puppies/fw-modularbed.bin" => Ok(Self::ModularBedResourcePath),
            "/puppies/fw-xbuddy-extension.bin" => Ok(Self::XBuddyExtensionResourcePath),
            "/mmu/fw.bin" => Ok(Self::MmuFirmwareResourcePath),
            _ => Err(InvariantError::InvalidFirmwareImageSource),
        }
    }

    /// Returns the manifest string for this named source.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::DwarfBinaryPath => "DWARF_BINARY_PATH",
            Self::ModularBedBinaryPath => "MODULARBED_BINARY_PATH",
            Self::XBuddyExtensionBinaryPath => "XBUDDY_EXTENSION_BINARY_PATH",
            Self::DwarfResourcePath => "/puppies/fw-dwarf.bin",
            Self::ModularBedResourcePath => "/puppies/fw-modularbed.bin",
            Self::XBuddyExtensionResourcePath => "/puppies/fw-xbuddy-extension.bin",
            Self::MmuFirmwareResourcePath => "/mmu/fw.bin",
        }
    }
}

/// Auxiliary firmware update or packaging mode.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum AuxiliaryUpdateMode {
    /// Flash auxiliary firmware at startup.
    StartupFlash,
    /// Skip auxiliary flashing.
    SkipFlash,
    /// Use a prebuilt firmware path.
    PrebuiltPath,
    /// Use a firmware descriptor.
    FirmwareDescriptor,
    /// Download a crash dump from an auxiliary controller.
    CrashDumpDownload,
    /// Run an MMU bootloader update.
    MmuBootloaderUpdate,
}

impl AuxiliaryUpdateMode {
    /// Parses an auxiliary update mode string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "startup-flash" => Ok(Self::StartupFlash),
            "skip-flash" => Ok(Self::SkipFlash),
            "prebuilt-path" => Ok(Self::PrebuiltPath),
            "firmware-descriptor" => Ok(Self::FirmwareDescriptor),
            "crash-dump-download" => Ok(Self::CrashDumpDownload),
            "mmu-bootloader-update" => Ok(Self::MmuBootloaderUpdate),
            _ => Err(InvariantError::InvalidAuxiliaryUpdateMode),
        }
    }

    /// Returns the manifest string for this update mode.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::StartupFlash => "startup-flash",
            Self::SkipFlash => "skip-flash",
            Self::PrebuiltPath => "prebuilt-path",
            Self::FirmwareDescriptor => "firmware-descriptor",
            Self::CrashDumpDownload => "crash-dump-download",
            Self::MmuBootloaderUpdate => "mmu-bootloader-update",
        }
    }
}

/// Valid Modbus unit identity for auxiliary bus contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ModbusUnitIdentity(u8);

impl ModbusUnitIdentity {
    /// Creates a Modbus unit identity in the valid unit range.
    pub fn new(unit: u8) -> Result<Self, InvariantError> {
        if !(1..=247).contains(&unit) {
            return Err(InvariantError::InvalidModbusUnitIdentity);
        }

        Ok(Self(unit))
    }

    /// Returns the validated unit identity.
    pub fn as_u8(self) -> u8 {
        self.0
    }
}

/// Modbus request kind preserved by auxiliary parity contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ModbusRequestKind {
    /// Read input registers.
    ReadInput,
    /// Read holding registers.
    ReadHolding,
    /// Write holding registers.
    WriteHolding,
    /// Write a coil.
    WriteCoil,
    /// Read FIFO data.
    ReadFifo,
    /// Query request.
    Query,
    /// Command request.
    Command,
}

impl ModbusRequestKind {
    /// Parses a Modbus request kind string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "read-input" => Ok(Self::ReadInput),
            "read-holding" => Ok(Self::ReadHolding),
            "write-holding" => Ok(Self::WriteHolding),
            "write-coil" => Ok(Self::WriteCoil),
            "read-fifo" => Ok(Self::ReadFifo),
            "query" => Ok(Self::Query),
            "command" => Ok(Self::Command),
            _ => Err(InvariantError::InvalidModbusRequestKind),
        }
    }

    /// Returns the manifest string for this request kind.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::ReadInput => "read-input",
            Self::ReadHolding => "read-holding",
            Self::WriteHolding => "write-holding",
            Self::WriteCoil => "write-coil",
            Self::ReadFifo => "read-fifo",
            Self::Query => "query",
            Self::Command => "command",
        }
    }
}

/// Evidence class for a Phase 10 auxiliary parity claim.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum BusEvidenceClass {
    /// Manifest structure and source paths are checked locally.
    ManifestCheck,
    /// Source audit against retained auxiliary paths.
    SourceAudit,
    /// Static source audit against retained boundary paths.
    StaticSourceAudit,
    /// Host test evidence in the retained or mixed codebase.
    HostTest,
    /// Rust host test evidence for pure Rust auxiliary classification.
    RustHostTest,
    /// Simulator flow evidence is required.
    SimulatorFlow,
    /// Hardware smoke evidence is required.
    HardwareSmoke,
    /// Manual hardware or failure-injection evidence is required.
    ManualHardwareRequired,
}

impl BusEvidenceClass {
    /// Parses a Phase 10 evidence class string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "manifest-check" => Ok(Self::ManifestCheck),
            "source-audit" => Ok(Self::SourceAudit),
            "static-source-audit" => Ok(Self::StaticSourceAudit),
            "host-test" => Ok(Self::HostTest),
            "rust-host-test" => Ok(Self::RustHostTest),
            "simulator-flow" => Ok(Self::SimulatorFlow),
            "hardware-smoke" => Ok(Self::HardwareSmoke),
            "manual-hardware-required" => Ok(Self::ManualHardwareRequired),
            _ => Err(InvariantError::InvalidBusEvidenceClass),
        }
    }

    /// Returns the manifest string for this evidence class.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::ManifestCheck => "manifest-check",
            Self::SourceAudit => "source-audit",
            Self::StaticSourceAudit => "static-source-audit",
            Self::HostTest => "host-test",
            Self::RustHostTest => "rust-host-test",
            Self::SimulatorFlow => "simulator-flow",
            Self::HardwareSmoke => "hardware-smoke",
            Self::ManualHardwareRequired => "manual-hardware-required",
        }
    }

    /// Returns whether this evidence class can support a local proof scope.
    pub fn is_local_proof(self) -> bool {
        !matches!(
            self,
            Self::SimulatorFlow | Self::HardwareSmoke | Self::ManualHardwareRequired
        )
    }
}

/// Locality scope for Phase 10 auxiliary proof.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum AuxiliaryProofScope {
    /// Locally provable by manifest, source, host, or Rust checks.
    Local,
    /// Requires simulator, hardware, update-flow, or manual evidence.
    NonLocal,
}

impl AuxiliaryProofScope {
    /// Parses a Phase 10 proof-scope string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "local" => Ok(Self::Local),
            "non-local" => Ok(Self::NonLocal),
            _ => Err(InvariantError::InvalidAuxiliaryProofScope),
        }
    }

    /// Returns the manifest string for this proof scope.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Local => "local",
            Self::NonLocal => "non-local",
        }
    }
}

/// MMU transport state represented by Phase 10 auxiliary contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum MmuTransportState {
    /// MMU transport is disabled.
    Disabled,
    /// MMU transport is unavailable.
    Unavailable,
    /// MMU transport is in bootloader mode.
    Bootloader,
    /// MMU transport is stopped.
    Stopped,
    /// MMU transport is active.
    Active,
    /// MMU transport is updating.
    Updating,
    /// MMU transport update failed.
    UpdateFailed,
    /// MMU communication fault is present.
    CommunicationFault,
}

impl MmuTransportState {
    /// Parses an MMU transport state string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "disabled" => Ok(Self::Disabled),
            "unavailable" => Ok(Self::Unavailable),
            "bootloader" => Ok(Self::Bootloader),
            "stopped" => Ok(Self::Stopped),
            "active" => Ok(Self::Active),
            "updating" => Ok(Self::Updating),
            "update-failed" => Ok(Self::UpdateFailed),
            "communication-fault" => Ok(Self::CommunicationFault),
            _ => Err(InvariantError::InvalidMmuTransportState),
        }
    }

    /// Returns the manifest string for this transport state.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Disabled => "disabled",
            Self::Unavailable => "unavailable",
            Self::Bootloader => "bootloader",
            Self::Stopped => "stopped",
            Self::Active => "active",
            Self::Updating => "updating",
            Self::UpdateFailed => "update-failed",
            Self::CommunicationFault => "communication-fault",
        }
    }
}

/// MMU transport surface represented by Phase 10 auxiliary contracts.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum MmuTransportSurface {
    /// MMU is connected over direct UART.
    Uart,
    /// MMU is bridged through puppy Modbus.
    PuppyModbusBridge,
}

impl MmuTransportSurface {
    /// Parses an MMU transport surface string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "direct-uart" => Ok(Self::Uart),
            "puppy-modbus-bridge" => Ok(Self::PuppyModbusBridge),
            _ => Err(InvariantError::InvalidMmuTransportSurface),
        }
    }

    /// Returns the manifest string for this transport surface.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Uart => "direct-uart",
            Self::PuppyModbusBridge => "puppy-modbus-bridge",
        }
    }
}

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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        BoardKind, BootloaderMode, Feature, FeatureSet, InvariantError, McuKind, PrinterKind,
        ProductProfile,
    };

    fn valid_row_id() -> AuxiliaryParityRowId {
        AuxiliaryParityRowId::parse("mmu2-availability-reporting-stub")
            .expect("test row ID is valid")
    }

    fn auxiliary_parity_input(
        evidence_class: BusEvidenceClass,
        proof_scope: AuxiliaryProofScope,
    ) -> AuxiliaryParityContractInput {
        AuxiliaryParityContractInput {
            row_id: valid_row_id(),
            evidence_class,
            proof_scope,
        }
    }

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
    fn parses_auxiliary_parity_row_ids() {
        // Arrange
        let valid_id = "mmu2-availability-reporting-stub";
        let oversized_id = "a".repeat(97);
        let invalid_ids = [
            "",
            ".",
            "..",
            "../mmu2",
            "mmu2\\availability",
            "mmu2 availability",
            "mmu2\navailability",
        ];

        // Act
        let valid_result = AuxiliaryParityRowId::parse(valid_id);
        let oversized_result = AuxiliaryParityRowId::parse(oversized_id);
        let invalid_results = invalid_ids.map(AuxiliaryParityRowId::parse);

        // Assert
        assert!(matches!(
            valid_result,
            Ok(row_id) if row_id.as_str() == valid_id
        ));
        assert_eq!(
            invalid_results[0],
            Err(InvariantError::EmptyAuxiliaryParityRowId)
        );
        assert!(invalid_results[1..].iter().all(Result::is_err));
        assert_eq!(
            oversized_result,
            Err(InvariantError::InvalidAuxiliaryParityRowId)
        );
    }

    #[test]
    fn classifies_bus_evidence_locality() {
        // Arrange
        let local_evidence = "manifest-check";
        let hardware_evidence = "hardware-smoke";
        let manual_evidence = "manual-hardware-required";

        // Act
        let local_result = BusEvidenceClass::parse(local_evidence);
        let hardware_result = BusEvidenceClass::parse(hardware_evidence);
        let manual_result = BusEvidenceClass::parse(manual_evidence);

        // Assert
        assert!(matches!(
            local_result,
            Ok(evidence_class)
                if evidence_class.as_str() == local_evidence && evidence_class.is_local_proof()
        ));
        assert!(matches!(
            hardware_result,
            Ok(evidence_class)
                if evidence_class.as_str() == hardware_evidence
                    && !evidence_class.is_local_proof()
        ));
        assert!(matches!(
            manual_result,
            Ok(evidence_class)
                if evidence_class.as_str() == manual_evidence && !evidence_class.is_local_proof()
        ));
    }

    #[test]
    fn rejects_non_local_bus_evidence_as_local_proof() {
        // Arrange
        let non_local_evidence_classes = [
            BusEvidenceClass::SimulatorFlow,
            BusEvidenceClass::HardwareSmoke,
            BusEvidenceClass::ManualHardwareRequired,
        ];

        // Act
        let results = non_local_evidence_classes.map(|evidence_class| {
            AuxiliaryParityContract::new(auxiliary_parity_input(
                evidence_class,
                AuxiliaryProofScope::Local,
            ))
        });

        // Assert
        assert!(
            results
                .iter()
                .all(|result| *result == Err(InvariantError::InvalidAuxiliaryParityContract))
        );
    }

    #[test]
    fn parses_all_auxiliary_runtime_states() {
        // Arrange
        let raw_states = [
            "bootloader",
            "unavailable",
            "active",
            "stopped",
            "updating",
            "update-failed",
            "communication-fault",
            "unknown-reference-deferred",
        ];

        // Act
        let results = raw_states.map(AuxiliaryRuntimeState::parse);

        // Assert
        assert!(results.iter().all(Result::is_ok));
    }

    #[test]
    fn keeps_firmware_image_sources_named_only() {
        // Arrange
        let raw_sources = [
            "DWARF_BINARY_PATH",
            "MODULARBED_BINARY_PATH",
            "XBUDDY_EXTENSION_BINARY_PATH",
            "/puppies/fw-dwarf.bin",
            "/puppies/fw-modularbed.bin",
            "/puppies/fw-xbuddy-extension.bin",
            "/mmu/fw.bin",
        ];

        // Act
        let results = raw_sources.map(FirmwareImageSource::parse);

        // Assert
        for (raw_source, result) in raw_sources.into_iter().zip(results) {
            assert!(matches!(result, Ok(source) if source.as_str() == raw_source));
        }
    }

    #[test]
    fn validates_modbus_unit_identity_bounds() {
        // Arrange
        let xbuddy_extension_mmu_bridge_unit = 220;

        // Act
        let valid_result = ModbusUnitIdentity::new(xbuddy_extension_mmu_bridge_unit);
        let zero_result = ModbusUnitIdentity::new(0);
        let broadcast_overflow_result = ModbusUnitIdentity::new(248);

        // Assert
        assert!(matches!(
            valid_result,
            Ok(identity) if identity.as_u8() == xbuddy_extension_mmu_bridge_unit
        ));
        assert_eq!(zero_result, Err(InvariantError::InvalidModbusUnitIdentity));
        assert_eq!(
            broadcast_overflow_result,
            Err(InvariantError::InvalidModbusUnitIdentity)
        );
    }

    #[test]
    fn parses_dock_identities() {
        // Arrange
        let raw_docks = ["DWARF_1", "DWARF_6", "MODULAR_BED", "XBUDDY_EXTENSION"];

        // Act
        let results = raw_docks.map(DockIdentity::parse);
        let unknown_result = DockIdentity::parse("UNKNOWN_DOCK");

        // Assert
        assert_eq!(
            results,
            [
                Ok(DockIdentity::Dwarf1),
                Ok(DockIdentity::Dwarf6),
                Ok(DockIdentity::ModularBed),
                Ok(DockIdentity::XBuddyExtension),
            ]
        );
        assert_eq!(unknown_result, Err(InvariantError::InvalidDockIdentity));
    }

    #[test]
    fn validates_tool_offset_identity_range() {
        // Arrange
        let first_tool = 1;
        let last_tool = 6;

        // Act
        let first_result = ToolOffsetIdentity::new(first_tool, ToolOffsetAxis::X);
        let last_result = ToolOffsetIdentity::new(last_tool, ToolOffsetAxis::Z);
        let zero_result = ToolOffsetIdentity::new(0, ToolOffsetAxis::Y);
        let overflow_result = ToolOffsetIdentity::new(7, ToolOffsetAxis::Y);

        // Assert
        assert!(matches!(
            first_result,
            Ok(identity)
                if identity.tool_number() == first_tool && identity.axis() == ToolOffsetAxis::X
        ));
        assert!(matches!(
            last_result,
            Ok(identity)
                if identity.tool_number() == last_tool && identity.axis() == ToolOffsetAxis::Z
        ));
        assert_eq!(zero_result, Err(InvariantError::InvalidToolOffsetIdentity));
        assert_eq!(
            overflow_result,
            Err(InvariantError::InvalidToolOffsetIdentity)
        );
    }

    #[test]
    fn parses_mmu_transport_states() {
        // Arrange
        let raw_states = [
            "disabled",
            "unavailable",
            "bootloader",
            "stopped",
            "active",
            "updating",
            "update-failed",
            "communication-fault",
        ];

        // Act
        let results = raw_states.map(MmuTransportState::parse);

        // Assert
        assert!(results.iter().all(Result::is_ok));
    }

    #[test]
    fn parses_mmu_transport_surfaces() {
        // Arrange
        let raw_surfaces = ["direct-uart", "puppy-modbus-bridge"];
        let unknown_surface = "availability-reporting-stub";

        // Act
        let results = raw_surfaces.map(MmuTransportSurface::parse);
        let unknown_result = MmuTransportSurface::parse(unknown_surface);

        // Assert
        assert!(matches!(
            results[0],
            Ok(surface) if surface.as_str() == raw_surfaces[0]
        ));
        assert!(matches!(
            results[1],
            Ok(surface) if surface.as_str() == raw_surfaces[1]
        ));
        assert_eq!(
            unknown_result,
            Err(InvariantError::InvalidMmuTransportSurface)
        );
    }

    #[test]
    fn parses_update_modes_and_modbus_request_kinds() {
        // Arrange
        let update_modes = [
            "startup-flash",
            "skip-flash",
            "prebuilt-path",
            "firmware-descriptor",
            "crash-dump-download",
            "mmu-bootloader-update",
        ];
        let request_kinds = [
            "read-input",
            "read-holding",
            "write-holding",
            "write-coil",
            "read-fifo",
            "query",
            "command",
        ];

        // Act
        let update_results = update_modes.map(AuxiliaryUpdateMode::parse);
        let request_results = request_kinds.map(ModbusRequestKind::parse);

        // Assert
        assert!(update_results.iter().all(Result::is_ok));
        assert!(request_results.iter().all(Result::is_ok));
    }

    #[test]
    fn gates_auxiliary_controller_by_product_profile() {
        // Arrange
        let dwarf_profile = profile(
            PrinterKind::Xl,
            BoardKind::Dwarf,
            McuKind::Stm32G070RbT6,
            BootloaderMode::Auxiliary,
            FeatureSet::from_features([Feature::Dwarf]),
        );
        let dwarf_input = AuxiliaryControllerContractInput {
            profile: dwarf_profile.clone(),
            controller_kind: AuxiliaryControllerKind::Dwarf,
        };
        let xbuddy_extension_input = AuxiliaryControllerContractInput {
            profile: dwarf_profile,
            controller_kind: AuxiliaryControllerKind::XBuddyExtension,
        };

        // Act
        let dwarf_result = AuxiliaryControllerContract::new(dwarf_input);
        let mismatch_result = AuxiliaryControllerContract::new(xbuddy_extension_input);

        // Assert
        assert!(matches!(
            dwarf_result,
            Ok(contract) if contract.controller_kind() == AuxiliaryControllerKind::Dwarf
        ));
        assert_eq!(
            mismatch_result,
            Err(InvariantError::UnsupportedAuxiliaryController)
        );
    }

    #[test]
    fn parses_controller_fault_classes() {
        // Arrange
        let raw_faults = [
            "fingerprint-mismatch",
            "modbus-communication",
            "dwarf-tmc",
            "modular-bed-panic",
            "xbuddy-extension-mmu-bridge",
        ];

        // Act
        let results = raw_faults.map(ControllerFaultClass::parse);

        // Assert
        assert_eq!(
            results,
            [
                Ok(ControllerFaultClass::FingerprintMismatch),
                Ok(ControllerFaultClass::ModbusCommunication),
                Ok(ControllerFaultClass::DwarfTmc),
                Ok(ControllerFaultClass::ModularBedPanic),
                Ok(ControllerFaultClass::XBuddyExtensionMmuBridge),
            ]
        );
    }
}
