use crate::{Feature, FeatureSet, InvariantError};

fn is_path_free_printable_ascii(raw: &str) -> bool {
    raw != "."
        && raw != ".."
        && !raw.contains('/')
        && !raw.contains('\\')
        && raw.bytes().all(|byte| byte.is_ascii_graphic())
}

fn is_valid_short_identity(raw: &str) -> bool {
    !raw.is_empty() && raw.len() <= 96 && is_path_free_printable_ascii(raw)
}

/// Evidence class for a Phase 9 network, web-service, or transfer parity claim.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum NetworkEvidenceClass {
    /// Manifest structure and source paths are checked locally.
    ManifestCheck,
    /// Source audit against retained network paths.
    SourceAudit,
    /// Static source audit against retained boundary paths.
    StaticSourceAudit,
    /// Host test evidence in the retained or mixed codebase.
    HostTest,
    /// Rust host test evidence for pure Rust network classification.
    RustHostTest,
    /// Existing unit-test-backed compatibility evidence.
    UnitTestBacked,
    /// Simulator flow evidence is required.
    SimulatorFlow,
    /// Hardware smoke evidence is required.
    HardwareSmoke,
    /// Manual hardware or failure-injection evidence is required.
    ManualHardwareRequired,
}

impl NetworkEvidenceClass {
    /// Parses a Phase 9 evidence class string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "manifest-check" => Ok(Self::ManifestCheck),
            "source-audit" => Ok(Self::SourceAudit),
            "static-source-audit" => Ok(Self::StaticSourceAudit),
            "host-test" => Ok(Self::HostTest),
            "rust-host-test" => Ok(Self::RustHostTest),
            "unit-test-backed" => Ok(Self::UnitTestBacked),
            "simulator-flow" => Ok(Self::SimulatorFlow),
            "hardware-smoke" => Ok(Self::HardwareSmoke),
            "manual-hardware-required" => Ok(Self::ManualHardwareRequired),
            _ => Err(InvariantError::InvalidNetworkEvidenceClass),
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
            Self::UnitTestBacked => "unit-test-backed",
            Self::SimulatorFlow => "simulator-flow",
            Self::HardwareSmoke => "hardware-smoke",
            Self::ManualHardwareRequired => "manual-hardware-required",
        }
    }

    /// Returns whether this evidence class can support a local proof scope.
    pub fn is_local_proof(self) -> bool {
        matches!(
            self,
            Self::ManifestCheck
                | Self::SourceAudit
                | Self::StaticSourceAudit
                | Self::HostTest
                | Self::RustHostTest
                | Self::UnitTestBacked
        )
    }
}

/// Locality scope for Phase 9 proof.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum NetworkProofScope {
    /// Locally provable by manifest, source, host, or Rust checks.
    Local,
    /// Requires simulator, hardware, live cloud, media, or manual evidence.
    NonLocal,
}

impl NetworkProofScope {
    /// Parses a Phase 9 proof-scope string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "local" => Ok(Self::Local),
            "non-local" => Ok(Self::NonLocal),
            _ => Err(InvariantError::InvalidNetworkProofScope),
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

/// Phase 9 parity row identity parsed before verifier or adapter code uses it.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct NetworkParityRowId(String);

impl NetworkParityRowId {
    /// Parses a path-free printable ASCII row ID at most 96 bytes long.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(InvariantError::EmptyNetworkParityRowId);
        }

        if !is_valid_short_identity(&raw) {
            return Err(InvariantError::InvalidNetworkParityRowId);
        }

        Ok(Self(raw))
    }

    /// Returns the validated row ID as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Policy for credential-bearing Phase 9 evidence.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum SecretHandling {
    /// The row contains no credential-bearing identity.
    None,
    /// The row may name a credential identity but must not contain value bytes.
    NamedOnlyRedacted,
}

impl SecretHandling {
    /// Parses a secret-handling value.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "none" => Ok(Self::None),
            "named-only-redacted" => Ok(Self::NamedOnlyRedacted),
            _ => Err(InvariantError::InvalidSecretHandling),
        }
    }

    /// Returns the manifest string for this policy.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::NamedOnlyRedacted => "named-only-redacted",
        }
    }

    /// Returns whether this policy permits credential value material.
    pub fn allows_value_material(self) -> bool {
        match self {
            Self::None => false,
            Self::NamedOnlyRedacted => false,
        }
    }
}

/// Connect identity surface named without embedding secret values.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ConnectIdentity {
    /// Persistent Connect token config key identity.
    TokenConfigKey,
    /// HTTP fingerprint header identity.
    FingerprintHeader,
    /// Registration-code header identity.
    RegistrationCodeHeader,
}

impl ConnectIdentity {
    /// Returns the manifest string for this identity.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::TokenConfigKey => "token-config-key",
            Self::FingerprintHeader => "fingerprint-header",
            Self::RegistrationCodeHeader => "registration-code-header",
        }
    }
}

/// Connect command identifier parsed before command handling.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ConnectCommandId(String);

impl ConnectCommandId {
    /// Parses a path-free printable ASCII command ID at most 96 bytes long.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if !is_valid_short_identity(&raw) {
            return Err(InvariantError::InvalidConnectCommandId);
        }

        Ok(Self(raw))
    }

    /// Returns the validated command ID as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Retained Connect command state classification.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ConnectCommandState {
    /// Command has not started yet.
    Pending,
    /// Command is being processed.
    InProgress,
    /// Command finished successfully.
    Finished,
    /// Command was rejected.
    Rejected,
    /// Command was rejected as a duplicate.
    Duplicate,
    /// Command exceeded retained size limits.
    Oversized,
    /// Command payload was malformed.
    BrokenCommand,
}

impl ConnectCommandState {
    /// Parses a Connect command state string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "pending" => Ok(Self::Pending),
            "in-progress" => Ok(Self::InProgress),
            "finished" => Ok(Self::Finished),
            "rejected" => Ok(Self::Rejected),
            "duplicate" => Ok(Self::Duplicate),
            "oversized" => Ok(Self::Oversized),
            "broken-command" => Ok(Self::BrokenCommand),
            _ => Err(InvariantError::InvalidConnectCommandState),
        }
    }

    /// Returns the manifest string for this state.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Pending => "pending",
            Self::InProgress => "in-progress",
            Self::Finished => "finished",
            Self::Rejected => "rejected",
            Self::Duplicate => "duplicate",
            Self::Oversized => "oversized",
            Self::BrokenCommand => "broken-command",
        }
    }
}

/// Connect telemetry and event publication surface.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum TelemetryEventSurface {
    /// Telemetry payload surface.
    Telemetry,
    /// Event payload surface.
    Event,
    /// Transfer information payload surface.
    TransferInfo,
    /// Transfer stopped event surface.
    TransferStopped,
    /// Transfer aborted event surface.
    TransferAborted,
    /// Transfer finished event surface.
    TransferFinished,
}

impl TelemetryEventSurface {
    /// Parses a telemetry or event surface string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "telemetry" => Ok(Self::Telemetry),
            "event" => Ok(Self::Event),
            "transfer-info" => Ok(Self::TransferInfo),
            "transfer-stopped" => Ok(Self::TransferStopped),
            "transfer-aborted" => Ok(Self::TransferAborted),
            "transfer-finished" => Ok(Self::TransferFinished),
            _ => Err(InvariantError::InvalidTelemetryEventSurface),
        }
    }

    /// Returns the manifest string for this surface.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Telemetry => "telemetry",
            Self::Event => "event",
            Self::TransferInfo => "transfer-info",
            Self::TransferStopped => "transfer-stopped",
            Self::TransferAborted => "transfer-aborted",
            Self::TransferFinished => "transfer-finished",
        }
    }
}

/// WebSocket command classification preserved from Connect behavior.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum WebSocketCommandState {
    /// Command was accepted.
    Accepted,
    /// Command was rejected as oversized.
    RejectedOversized,
    /// Command was rejected as duplicate.
    RejectedDuplicate,
    /// Command was malformed.
    BrokenCommand,
}

impl WebSocketCommandState {
    /// Parses a WebSocket command state string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "accepted" => Ok(Self::Accepted),
            "rejected-oversized" => Ok(Self::RejectedOversized),
            "rejected-duplicate" => Ok(Self::RejectedDuplicate),
            "broken-command" => Ok(Self::BrokenCommand),
            _ => Err(InvariantError::InvalidWebSocketCommandState),
        }
    }

    /// Returns the manifest string for this state.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Accepted => "accepted",
            Self::RejectedOversized => "rejected-oversized",
            Self::RejectedDuplicate => "rejected-duplicate",
            Self::BrokenCommand => "broken-command",
        }
    }
}

/// Connect proxy mode preserved as a compatibility contract.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum ProxyMode {
    /// Proxy support is disabled.
    Disabled,
    /// HTTP CONNECT proxy support is available only for TLS traffic.
    HttpConnectTlsOnly,
}

impl ProxyMode {
    /// Parses a proxy mode string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "disabled" => Ok(Self::Disabled),
            "http-connect-tls-only" => Ok(Self::HttpConnectTlsOnly),
            _ => Err(InvariantError::InvalidProxyMode),
        }
    }

    /// Returns the manifest string for this proxy mode.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Disabled => "disabled",
            Self::HttpConnectTlsOnly => "http-connect-tls-only",
        }
    }

    /// Returns whether this proxy mode requires TLS.
    pub fn requires_tls(self) -> bool {
        matches!(self, Self::HttpConnectTlsOnly)
    }

    /// Returns whether this proxy mode supports proxy authentication.
    pub fn supports_authentication(self) -> bool {
        false
    }
}

/// PrusaLink/WUI endpoint family.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum WuiEndpointFamily {
    /// PrusaLink API v1 endpoints.
    PrusaLinkApiV1,
    /// OctoPrint-compatible API endpoints.
    OctoPrintCompatible,
    /// Static web UI assets.
    StaticAssets,
    /// USB file handlers.
    UsbFiles,
    /// Transfer endpoints.
    Transfer,
    /// Preview endpoints.
    Preview,
    /// Unknown request handling.
    UnknownRequest,
}

impl WuiEndpointFamily {
    /// Parses a WUI endpoint family string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "prusa-link-api-v1" => Ok(Self::PrusaLinkApiV1),
            "octoprint-compatible" => Ok(Self::OctoPrintCompatible),
            "static-assets" => Ok(Self::StaticAssets),
            "usb-files" => Ok(Self::UsbFiles),
            "transfer" => Ok(Self::Transfer),
            "preview" => Ok(Self::Preview),
            "unknown-request" => Ok(Self::UnknownRequest),
            _ => Err(InvariantError::InvalidWuiEndpointFamily),
        }
    }

    /// Returns the manifest string for this endpoint family.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::PrusaLinkApiV1 => "prusa-link-api-v1",
            Self::OctoPrintCompatible => "octoprint-compatible",
            Self::StaticAssets => "static-assets",
            Self::UsbFiles => "usb-files",
            Self::Transfer => "transfer",
            Self::Preview => "preview",
            Self::UnknownRequest => "unknown-request",
        }
    }
}

/// Authentication mode used by WUI, PrusaLink, Connect, or credential surfaces.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum WuiAuthMode {
    /// No authentication is required.
    None,
    /// Digest authentication.
    Digest,
    /// API key authentication.
    ApiKey,
    /// Connect token identity.
    ConnectToken,
    /// On-device credential display identity.
    CredentialDisplay,
    /// Named secret identity without value material.
    NamedOnlySecret,
}

impl WuiAuthMode {
    /// Parses a WUI auth mode string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "none" => Ok(Self::None),
            "digest" => Ok(Self::Digest),
            "api-key" => Ok(Self::ApiKey),
            "connect-token" => Ok(Self::ConnectToken),
            "credential-display" => Ok(Self::CredentialDisplay),
            "named-only-secret" => Ok(Self::NamedOnlySecret),
            _ => Err(InvariantError::InvalidWuiAuthMode),
        }
    }

    /// Returns the manifest string for this auth mode.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::Digest => "digest",
            Self::ApiKey => "api-key",
            Self::ConnectToken => "connect-token",
            Self::CredentialDisplay => "credential-display",
            Self::NamedOnlySecret => "named-only-secret",
        }
    }
}

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

/// Product-gated Phase 9 network service surface.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum NetworkServiceSurface {
    /// Prusa Connect client surface.
    PrusaConnect,
    /// PrusaLink/WUI local service surface.
    PrusaLinkWui,
    /// SNTP service surface.
    Sntp,
    /// mDNS service surface.
    Mdns,
    /// DNS resolver service surface.
    Dns,
    /// Metrics UDP service surface.
    Metrics,
    /// Syslog UDP service surface.
    Syslog,
}

impl NetworkServiceSurface {
    /// Parses a network service surface string.
    pub fn parse(raw: &str) -> Result<Self, InvariantError> {
        match raw {
            "prusa-connect" => Ok(Self::PrusaConnect),
            "prusa-link-wui" => Ok(Self::PrusaLinkWui),
            "sntp" => Ok(Self::Sntp),
            "mdns" => Ok(Self::Mdns),
            "dns" => Ok(Self::Dns),
            "metrics" => Ok(Self::Metrics),
            "syslog" => Ok(Self::Syslog),
            _ => Err(InvariantError::InvalidNetworkServiceSurface),
        }
    }

    /// Returns the manifest string for this surface.
    pub fn as_str(self) -> &'static str {
        match self {
            Self::PrusaConnect => "prusa-connect",
            Self::PrusaLinkWui => "prusa-link-wui",
            Self::Sntp => "sntp",
            Self::Mdns => "mdns",
            Self::Dns => "dns",
            Self::Metrics => "metrics",
            Self::Syslog => "syslog",
        }
    }
}

/// Raw inputs for creating a [`NetworkServiceContract`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NetworkServiceContractInput {
    /// Network service surface.
    pub surface: NetworkServiceSurface,
    /// Product feature set available for this service contract.
    pub features: FeatureSet,
}

/// Product-feature-gated network service contract.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NetworkServiceContract {
    surface: NetworkServiceSurface,
    features: FeatureSet,
}

impl NetworkServiceContract {
    /// Creates a service contract when the required feature is enabled.
    pub fn new(
        surface: NetworkServiceSurface,
        features: FeatureSet,
    ) -> Result<Self, InvariantError> {
        Self::from_input(NetworkServiceContractInput { surface, features })
    }

    /// Creates a service contract from raw validated input.
    pub fn from_input(input: NetworkServiceContractInput) -> Result<Self, InvariantError> {
        let NetworkServiceContractInput { surface, features } = input;
        let required_features: &[Feature] = match surface {
            NetworkServiceSurface::PrusaConnect => &[Feature::Connect, Feature::WebUi],
            NetworkServiceSurface::PrusaLinkWui
            | NetworkServiceSurface::Sntp
            | NetworkServiceSurface::Mdns
            | NetworkServiceSurface::Dns
            | NetworkServiceSurface::Metrics
            | NetworkServiceSurface::Syslog => &[Feature::WebUi],
        };

        if required_features
            .iter()
            .any(|feature| !features.contains(*feature))
        {
            return Err(InvariantError::UnsupportedNetworkService);
        }

        Ok(Self { surface, features })
    }

    /// Returns the service surface.
    pub fn surface(&self) -> NetworkServiceSurface {
        self.surface
    }

    /// Returns the feature set used to validate the service.
    pub fn features(&self) -> &FeatureSet {
        &self.features
    }
}

/// Raw inputs for creating a [`NetworkParityContract`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NetworkParityContractInput {
    /// Phase 9 row identity.
    pub row_id: NetworkParityRowId,
    /// Evidence class.
    pub evidence_class: NetworkEvidenceClass,
    /// Proof scope.
    pub proof_scope: NetworkProofScope,
    /// Secret handling policy.
    pub secret_handling: SecretHandling,
}

/// Validated Phase 9 network parity row contract.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NetworkParityContract {
    row_id: NetworkParityRowId,
    evidence_class: NetworkEvidenceClass,
    proof_scope: NetworkProofScope,
    secret_handling: SecretHandling,
}

impl NetworkParityContract {
    /// Creates a parity contract when evidence/proof compatibility is valid.
    pub fn new(input: NetworkParityContractInput) -> Result<Self, InvariantError> {
        let NetworkParityContractInput {
            row_id,
            evidence_class,
            proof_scope,
            secret_handling,
        } = input;

        if matches!(proof_scope, NetworkProofScope::Local) && !evidence_class.is_local_proof() {
            return Err(InvariantError::InvalidNetworkProofScope);
        }

        Ok(Self {
            row_id,
            evidence_class,
            proof_scope,
            secret_handling,
        })
    }

    /// Returns the row ID.
    pub fn row_id(&self) -> &NetworkParityRowId {
        &self.row_id
    }

    /// Returns the evidence class.
    pub fn evidence_class(&self) -> NetworkEvidenceClass {
        self.evidence_class
    }

    /// Returns the proof scope.
    pub fn proof_scope(&self) -> NetworkProofScope {
        self.proof_scope
    }

    /// Returns the secret-handling policy.
    pub fn secret_handling(&self) -> SecretHandling {
        self.secret_handling
    }

    /// Returns whether this contract permits credential value material.
    pub fn allows_value_material(&self) -> bool {
        self.secret_handling.allows_value_material()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{Feature, FeatureSet, InvariantError};

    fn valid_row_id() -> NetworkParityRowId {
        NetworkParityRowId::parse("connect-registration-token-fingerprint")
            .expect("test row ID is valid")
    }

    fn network_parity_input(
        evidence_class: NetworkEvidenceClass,
        proof_scope: NetworkProofScope,
    ) -> NetworkParityContractInput {
        NetworkParityContractInput {
            row_id: valid_row_id(),
            evidence_class,
            proof_scope,
            secret_handling: SecretHandling::None,
        }
    }

    #[test]
    fn parses_network_evidence_classes() {
        // Arrange
        let local_evidence = "manifest-check";
        let unit_test_evidence = "unit-test-backed";
        let non_local_evidence = "simulator-flow";

        // Act
        let local_result = NetworkEvidenceClass::parse(local_evidence);
        let unit_test_result = NetworkEvidenceClass::parse(unit_test_evidence);
        let non_local_result = NetworkEvidenceClass::parse(non_local_evidence);

        // Assert
        assert!(matches!(
            local_result,
            Ok(evidence_class)
                if evidence_class.as_str() == local_evidence && evidence_class.is_local_proof()
        ));
        assert!(matches!(
            unit_test_result,
            Ok(evidence_class)
                if evidence_class.as_str() == unit_test_evidence
                    && evidence_class.is_local_proof()
        ));
        assert!(matches!(
            non_local_result,
            Ok(evidence_class)
                if evidence_class.as_str() == non_local_evidence
                    && !evidence_class.is_local_proof()
        ));
    }

    #[test]
    fn rejects_non_local_network_evidence_as_local_proof() {
        // Arrange
        let non_local_evidence_classes = [
            NetworkEvidenceClass::SimulatorFlow,
            NetworkEvidenceClass::HardwareSmoke,
            NetworkEvidenceClass::ManualHardwareRequired,
        ];

        // Act
        let results = non_local_evidence_classes.map(|evidence_class| {
            NetworkParityContract::new(network_parity_input(
                evidence_class,
                NetworkProofScope::Local,
            ))
        });

        // Assert
        assert!(
            results
                .iter()
                .all(|result| *result == Err(InvariantError::InvalidNetworkProofScope))
        );
    }

    #[test]
    fn rejects_invalid_network_parity_row_ids() {
        // Arrange
        let valid_id = "connect-registration-token-fingerprint";
        let oversized_id = "a".repeat(97);
        let invalid_ids = [
            "",
            "../connect",
            "connect\\token",
            "connect token",
            "connect\nid",
        ];

        // Act
        let valid_result = NetworkParityRowId::parse(valid_id);
        let oversized_result = NetworkParityRowId::parse(oversized_id);
        let invalid_results = invalid_ids.map(NetworkParityRowId::parse);

        // Assert
        assert!(matches!(
            valid_result,
            Ok(row_id) if row_id.as_str() == valid_id
        ));
        assert_eq!(
            invalid_results[0],
            Err(InvariantError::EmptyNetworkParityRowId)
        );
        assert!(invalid_results[1..].iter().all(Result::is_err));
        assert_eq!(
            oversized_result,
            Err(InvariantError::InvalidNetworkParityRowId)
        );
    }

    #[test]
    fn keeps_secret_handling_named_only() {
        // Arrange
        let raw_no_secret_handling = "none";
        let raw_secret_handling = "named-only-redacted";

        // Act
        let no_secret_result = SecretHandling::parse(raw_no_secret_handling);
        let result = SecretHandling::parse(raw_secret_handling);

        // Assert
        assert!(matches!(
            no_secret_result,
            Ok(secret_handling)
                if secret_handling.as_str() == raw_no_secret_handling
                    && !secret_handling.allows_value_material()
        ));
        assert!(matches!(
            result,
            Ok(secret_handling)
                if secret_handling.as_str() == raw_secret_handling
                    && !secret_handling.allows_value_material()
        ));
    }

    #[test]
    fn parses_connect_command_ids() {
        // Arrange
        let valid_id = "START_CONNECT_DOWNLOAD";
        let oversized_id = "A".repeat(97);
        let invalid_ids = ["", "../START", "START CONNECT", "START\nCONNECT"];

        // Act
        let valid_result = ConnectCommandId::parse(valid_id);
        let oversized_result = ConnectCommandId::parse(oversized_id);
        let invalid_results = invalid_ids.map(ConnectCommandId::parse);

        // Assert
        assert!(matches!(
            valid_result,
            Ok(command_id) if command_id.as_str() == valid_id
        ));
        assert!(
            invalid_results
                .iter()
                .all(|result| *result == Err(InvariantError::InvalidConnectCommandId))
        );
        assert_eq!(
            oversized_result,
            Err(InvariantError::InvalidConnectCommandId)
        );
    }

    #[test]
    fn preserves_proxy_tls_only_limitations() {
        // Arrange
        let raw_proxy_mode = "http-connect-tls-only";

        // Act
        let result = ProxyMode::parse(raw_proxy_mode);

        // Assert
        assert!(matches!(
            result,
            Ok(proxy_mode)
                if proxy_mode.as_str() == raw_proxy_mode
                    && proxy_mode.requires_tls()
                    && !proxy_mode.supports_authentication()
        ));
    }

    #[test]
    fn parses_wui_auth_modes() {
        // Arrange
        let raw_modes = ["digest", "api-key", "named-only-secret"];

        // Act
        let results = raw_modes.map(WuiAuthMode::parse);

        // Assert
        assert_eq!(
            results,
            [
                Ok(WuiAuthMode::Digest),
                Ok(WuiAuthMode::ApiKey),
                Ok(WuiAuthMode::NamedOnlySecret),
            ]
        );
    }

    #[test]
    fn rejects_invalid_transfer_range() {
        // Arrange
        let start = 100;

        // Act
        let invalid_result = TransferRange::new(start, Some(99));
        let open_ended_result = TransferRange::new(start, None);

        // Assert
        assert_eq!(invalid_result, Err(InvariantError::InvalidTransferRange));
        assert!(matches!(
            open_ended_result,
            Ok(range) if range.start() == start && range.maybe_inclusive_end().is_none()
        ));
    }

    #[test]
    fn stores_encrypted_payload_metadata_without_key_bytes() {
        // Arrange
        let key_identity = "transfer-key-id";

        // Act
        let metadata = EncryptedPayloadMetadata::aes_ctr_named_only(key_identity);

        // Assert
        assert!(matches!(
            metadata,
            Ok(metadata)
                if metadata.encryption_mode() == TransferEncryptionMode::AesCtr
                    && metadata.key_identity() == Some(key_identity)
                    && !metadata.allows_value_material()
        ));
    }

    #[test]
    fn gates_connect_service_by_feature() {
        // Arrange
        let connect_features = FeatureSet::from_features([Feature::Connect]);
        let connect_with_wui_features =
            FeatureSet::from_features([Feature::Connect, Feature::WebUi]);

        // Act
        let missing_feature_result =
            NetworkServiceContract::new(NetworkServiceSurface::PrusaConnect, FeatureSet::empty());
        let missing_wui_result =
            NetworkServiceContract::new(NetworkServiceSurface::PrusaConnect, connect_features);
        let enabled_result = NetworkServiceContract::new(
            NetworkServiceSurface::PrusaConnect,
            connect_with_wui_features,
        );

        // Assert
        assert_eq!(
            missing_feature_result,
            Err(InvariantError::UnsupportedNetworkService)
        );
        assert_eq!(
            missing_wui_result,
            Err(InvariantError::UnsupportedNetworkService)
        );
        assert!(matches!(
            enabled_result,
            Ok(contract) if contract.surface() == NetworkServiceSurface::PrusaConnect
        ));
    }

    #[test]
    fn gates_wui_and_local_services_by_feature() {
        // Arrange
        let web_ui_features = FeatureSet::from_features([Feature::WebUi]);
        let surfaces = [
            NetworkServiceSurface::PrusaLinkWui,
            NetworkServiceSurface::Sntp,
            NetworkServiceSurface::Mdns,
            NetworkServiceSurface::Dns,
            NetworkServiceSurface::Metrics,
            NetworkServiceSurface::Syslog,
        ];

        // Act
        let missing_feature_results =
            surfaces.map(|surface| NetworkServiceContract::new(surface, FeatureSet::empty()));
        let enabled_results =
            surfaces.map(|surface| NetworkServiceContract::new(surface, web_ui_features.clone()));

        // Assert
        assert!(
            missing_feature_results
                .iter()
                .all(|result| *result == Err(InvariantError::UnsupportedNetworkService))
        );
        assert!(enabled_results.iter().all(
            |result| matches!(result, Ok(contract) if surfaces.contains(&contract.surface()))
        ));
    }

    #[test]
    fn exposes_planned_network_contract_surfaces() {
        // Arrange
        let _connect_identity = ConnectIdentity::TokenConfigKey;
        let _connect_command_state = ConnectCommandState::Pending;
        let _telemetry_surface = TelemetryEventSurface::Telemetry;
        let _websocket_state = WebSocketCommandState::Accepted;
        let _endpoint_family = WuiEndpointFamily::PrusaLinkApiV1;
        let _transfer_source = TransferSource::ConnectCommand;
        let _transfer_slot_state = TransferSlotState::Idle;
        let _transfer_recovery_state = TransferRecoveryState::NotNeeded;
        let _transfer_error_class = TransferErrorClass::Storage;
        let _service_input = NetworkServiceContractInput {
            surface: NetworkServiceSurface::PrusaConnect,
            features: FeatureSet::from_features([Feature::Connect]),
        };

        // Act
        let proof_scope = NetworkProofScope::parse("non-local");

        // Assert
        assert_eq!(proof_scope, Ok(NetworkProofScope::NonLocal));
    }
}
