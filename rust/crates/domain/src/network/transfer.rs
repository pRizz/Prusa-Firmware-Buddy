use super::identity::is_valid_short_identity;
use crate::InvariantError;

/// Entry point that initiated a transfer.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum TransferSource {
    /// Transfer started from a Connect command.
    ConnectCommand,
    /// Transfer started from a WUI upload.
    WuiUpload,
    /// Transfer started from the PrusaLink API.
    PrusaLinkApi,
    /// Transfer started from an OctoPrint-compatible API.
    OctoPrintApi,
    /// Transfer started by recovery flow.
    Recovery,
}

impl TransferSource {
    /// Parses a transfer source string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "connect-command" => Ok(Self::ConnectCommand),
            "wui-upload" => Ok(Self::WuiUpload),
            "prusa-link-api" => Ok(Self::PrusaLinkApi),
            "octoprint-api" => Ok(Self::OctoPrintApi),
            "recovery" => Ok(Self::Recovery),
            _ => Err(InvariantError::InvalidTransferSource),
        }
    }

    /// Returns the manifest string for this source.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::ConnectCommand => "connect-command",
            Self::WuiUpload => "wui-upload",
            Self::PrusaLinkApi => "prusa-link-api",
            Self::OctoPrintApi => "octoprint-api",
            Self::Recovery => "recovery",
        }
    }
}

/// Single transfer slot state preserved from the retained monitor model.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum TransferSlotState {
    /// No transfer is active.
    Idle,
    /// Slot has been reserved.
    Reserved,
    /// Download is active.
    Downloading,
    /// Upload is active.
    Uploading,
    /// Recovery is active.
    Recovering,
    /// Transfer finished.
    Finished,
    /// Transfer failed because of storage.
    ErrorStorage,
    /// Transfer failed because of networking.
    ErrorNetwork,
    /// Transfer failed for another retained reason.
    ErrorOther,
    /// Transfer was stopped.
    Stopped,
}

impl TransferSlotState {
    /// Parses a transfer slot state string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "idle" => Ok(Self::Idle),
            "reserved" => Ok(Self::Reserved),
            "downloading" => Ok(Self::Downloading),
            "uploading" => Ok(Self::Uploading),
            "recovering" => Ok(Self::Recovering),
            "finished" => Ok(Self::Finished),
            "error-storage" => Ok(Self::ErrorStorage),
            "error-network" => Ok(Self::ErrorNetwork),
            "error-other" => Ok(Self::ErrorOther),
            "stopped" => Ok(Self::Stopped),
            _ => Err(InvariantError::InvalidTransferSlotState),
        }
    }

    /// Returns the manifest string for this state.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Idle => "idle",
            Self::Reserved => "reserved",
            Self::Downloading => "downloading",
            Self::Uploading => "uploading",
            Self::Recovering => "recovering",
            Self::Finished => "finished",
            Self::ErrorStorage => "error-storage",
            Self::ErrorNetwork => "error-network",
            Self::ErrorOther => "error-other",
            Self::Stopped => "stopped",
        }
    }
}

/// Inclusive transfer byte range.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct TransferRange {
    start: u64,
    maybe_inclusive_end: Option<u64>,
}

impl TransferRange {
    /// Creates a range only when the optional inclusive end is not before the start.
    pub fn new(start: u64, maybe_inclusive_end: Option<u64>) -> Result<Self, InvariantError> {
        if maybe_inclusive_end.is_some_and(|inclusive_end| inclusive_end < start) {
            return Err(InvariantError::InvalidTransferRange);
        }

        Ok(Self {
            start,
            maybe_inclusive_end,
        })
    }

    /// Returns the first byte in the range.
    pub fn start(self) -> u64 {
        self.start
    }

    /// Returns the optional inclusive end byte.
    pub fn maybe_inclusive_end(self) -> Option<u64> {
        self.maybe_inclusive_end
    }
}

/// Transfer encryption mode.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum TransferEncryptionMode {
    /// Payload is not encrypted.
    None,
    /// Payload uses AES-CTR metadata.
    AesCtr,
}

impl TransferEncryptionMode {
    /// Parses a transfer encryption mode string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "none" => Ok(Self::None),
            "aes-ctr" => Ok(Self::AesCtr),
            _ => Err(InvariantError::InvalidTransferEncryptionMode),
        }
    }

    /// Returns the manifest string for this mode.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::AesCtr => "aes-ctr",
        }
    }
}

/// Encrypted payload metadata that stores identity only, never key or IV bytes.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EncryptedPayloadMetadata {
    encryption_mode: TransferEncryptionMode,
    maybe_key_identity: Option<String>,
}

impl EncryptedPayloadMetadata {
    /// Creates metadata for an unencrypted payload.
    pub fn none() -> Self {
        Self {
            encryption_mode: TransferEncryptionMode::None,
            maybe_key_identity: None,
        }
    }

    /// Creates AES-CTR metadata from a non-empty named key identity.
    pub fn aes_ctr_named_only(key_identity: impl Into<String>) -> Result<Self, InvariantError> {
        let key_identity = key_identity.into();
        if !is_valid_short_identity(&key_identity) {
            return Err(InvariantError::InvalidEncryptedPayloadMetadata);
        }

        Ok(Self {
            encryption_mode: TransferEncryptionMode::AesCtr,
            maybe_key_identity: Some(key_identity),
        })
    }

    /// Returns the encryption mode.
    pub fn encryption_mode(&self) -> TransferEncryptionMode {
        self.encryption_mode
    }

    /// Returns the key identity, when encrypted payload metadata named one.
    pub fn key_identity(&self) -> Option<&str> {
        self.maybe_key_identity.as_deref()
    }

    /// Returns whether this metadata permits key or IV value material.
    pub fn allows_value_material(&self) -> bool {
        false
    }
}

/// Transfer recovery state.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum TransferRecoveryState {
    /// Recovery is not needed.
    NotNeeded,
    /// Recovery waits for USB media.
    WaitingForUsb,
    /// Recovery is active.
    Recovering,
    /// Recovery finished.
    Finished,
    /// Recovery failed.
    Failed,
}

impl TransferRecoveryState {
    /// Parses a transfer recovery state string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "not-needed" => Ok(Self::NotNeeded),
            "waiting-for-usb" => Ok(Self::WaitingForUsb),
            "recovering" => Ok(Self::Recovering),
            "finished" => Ok(Self::Finished),
            "failed" => Ok(Self::Failed),
            _ => Err(InvariantError::InvalidTransferRecoveryState),
        }
    }

    /// Returns the manifest string for this state.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::NotNeeded => "not-needed",
            Self::WaitingForUsb => "waiting-for-usb",
            Self::Recovering => "recovering",
            Self::Finished => "finished",
            Self::Failed => "failed",
        }
    }
}

/// Transfer error class.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum TransferErrorClass {
    /// Storage failure.
    Storage,
    /// Network failure.
    Network,
    /// Cryptographic failure.
    Crypto,
    /// Range failure.
    Range,
    /// Media failure.
    Media,
    /// Other retained failure class.
    Other,
}

impl TransferErrorClass {
    /// Parses a transfer error class string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "storage" => Ok(Self::Storage),
            "network" => Ok(Self::Network),
            "crypto" => Ok(Self::Crypto),
            "range" => Ok(Self::Range),
            "media" => Ok(Self::Media),
            "other" => Ok(Self::Other),
            _ => Err(InvariantError::InvalidTransferErrorClass),
        }
    }

    /// Returns the manifest string for this class.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Storage => "storage",
            Self::Network => "network",
            Self::Crypto => "crypto",
            Self::Range => "range",
            Self::Media => "media",
            Self::Other => "other",
        }
    }
}
