use crate::InvariantError;

fn is_path_free_printable_ascii(raw: &str) -> bool {
    raw != "."
        && raw != ".."
        && !raw.contains('/')
        && !raw.contains('\\')
        && raw.bytes().all(|byte| byte.is_ascii_graphic())
}

pub(super) fn is_valid_short_identity(raw: &str) -> bool {
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
