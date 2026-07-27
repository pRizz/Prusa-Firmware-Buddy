use crate::InvariantError;

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
