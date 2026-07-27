use crate::InvariantError;

pub(super) fn is_valid_auxiliary_row_id(raw: &str) -> bool {
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
