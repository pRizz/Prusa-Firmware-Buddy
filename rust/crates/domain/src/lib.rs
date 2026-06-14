#![forbid(unsafe_code)]

//! Pure firmware domain model for the Rust port.
//!
//! This crate is the functional core for early Rust firmware decisions. It
//! encodes product, board, storage, artifact, and protocol invariants before
//! adapter code can use unchecked primitive values.

pub mod artifact;
pub mod auxiliary;
pub mod feature;
pub mod gui;
pub mod network;
pub mod print;
pub mod product;
pub mod protocol;
pub mod resource;
pub mod safety;
pub mod storage;

pub use artifact::{ArtifactFileName, ArtifactKind, ArtifactRequest};
pub use auxiliary::{
    AuxiliaryControllerContract, AuxiliaryControllerContractInput, AuxiliaryControllerKind,
    AuxiliaryParityContract, AuxiliaryParityContractInput, AuxiliaryParityRowId,
    AuxiliaryProofScope, AuxiliaryRuntimeState, AuxiliaryUpdateMode, BusEvidenceClass,
    ControllerFaultClass, DockIdentity, FirmwareImageSource, MmuTransportState, ModbusRequestKind,
    ModbusUnitIdentity, ToolOffsetAxis, ToolOffsetIdentity,
};
pub use feature::{
    BurstSteppingMode, Feature, FeatureSet, GateState, Phase6FeatureGate, Phase6FeatureGates,
};
pub use gui::{
    DisplayClass, GuiEvidenceClass, GuiParityContract, GuiParityContractInput, GuiParityRowId,
    GuiProofScope, GuiSemanticAction, GuiSurface, GuiWorkflow, IntentionalDeltaStatus,
    LocalizationSurface,
};
pub use network::{
    ConnectCommandId, ConnectCommandState, ConnectIdentity, EncryptedPayloadMetadata,
    NetworkEvidenceClass, NetworkParityContract, NetworkParityContractInput, NetworkParityRowId,
    NetworkProofScope, NetworkServiceContract, NetworkServiceContractInput, NetworkServiceSurface,
    ProxyMode, SecretHandling, TelemetryEventSurface, TransferEncryptionMode, TransferErrorClass,
    TransferRange, TransferRecoveryState, TransferSlotState, TransferSource, WebSocketCommandState,
    WuiAuthMode, WuiEndpointFamily,
};
pub use print::{
    CommandRoute, FixtureId, GcodeMnemonic, PlannerFlowState, PrintCommand, PrintJobState,
    PrintSource, PrintTransitionError, route_gcode_mnemonic, transition_print_state,
};
pub use product::{BoardKind, BootloaderMode, McuKind, PrinterKind, ProductProfile};
pub use protocol::{ConnectEndpoint, Connected, Disconnected, Registered, RegistrationCode};
pub use resource::{
    BazelLabel, GeneratedOutputOwnership, GeneratedSurface, ResourceRuntimePath, ResourceSurface,
};
pub use safety::{
    FatalPathPolicy, SafetyAction, SafetyFlow, SafetyPolicySurface, classify_safety_flow,
};
pub use storage::{
    CredentialRedactionPolicy, EvidenceClass, FilesystemSurface, FixtureIdentity, JournalHashFact,
    MigrationWindow, ReferenceHashName, StorageCompatibilityIdentity, StorageCompatibilitySurface,
    StorageKey, StorageSchemaVersion,
};

use core::fmt;

/// Error returned when raw firmware values do not satisfy domain invariants.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum InvariantError {
    /// The selected printer, board, MCU, or bootloader mode is not a supported
    /// reference combination.
    UnsupportedHardwareCombination {
        /// Selected printer.
        printer: PrinterKind,
        /// Selected board.
        board: BoardKind,
        /// Selected MCU.
        mcu: McuKind,
        /// Selected bootloader mode.
        bootloader_mode: BootloaderMode,
    },
    /// A feature flag was requested for a profile that cannot own it.
    UnsupportedFeature {
        /// Selected printer.
        printer: PrinterKind,
        /// Selected board.
        board: BoardKind,
        /// Requested feature.
        feature: Feature,
    },
    /// An auxiliary parity row ID was empty.
    EmptyAuxiliaryParityRowId,
    /// An auxiliary parity row ID contained unsupported syntax or characters.
    InvalidAuxiliaryParityRowId,
    /// An auxiliary controller kind was not recognized.
    InvalidAuxiliaryControllerKind,
    /// An auxiliary runtime state was not recognized.
    InvalidAuxiliaryRuntimeState,
    /// A firmware image source was not recognized.
    InvalidFirmwareImageSource,
    /// An auxiliary update mode was not recognized.
    InvalidAuxiliaryUpdateMode,
    /// A Modbus unit identity was outside the accepted unit range.
    InvalidModbusUnitIdentity,
    /// A Modbus request kind was not recognized.
    InvalidModbusRequestKind,
    /// A bus evidence class was not recognized.
    InvalidBusEvidenceClass,
    /// An auxiliary proof scope was not recognized.
    InvalidAuxiliaryProofScope,
    /// An MMU transport state was not recognized.
    InvalidMmuTransportState,
    /// A dock identity was not recognized.
    InvalidDockIdentity,
    /// A tool offset identity was outside the accepted range.
    InvalidToolOffsetIdentity,
    /// A controller fault class was not recognized.
    InvalidControllerFaultClass,
    /// An auxiliary parity contract paired an invalid proof scope with evidence.
    InvalidAuxiliaryParityContract,
    /// The selected product profile cannot own the requested auxiliary controller.
    UnsupportedAuxiliaryController,
    /// A file name was empty.
    EmptyArtifactName,
    /// A file name contained path syntax instead of a plain artifact name.
    ArtifactNameContainsPath,
    /// The artifact file suffix does not match the declared artifact kind.
    ArtifactSuffixMismatch {
        /// Declared artifact kind.
        kind: ArtifactKind,
        /// Required suffix for that kind.
        expected_suffix: &'static str,
    },
    /// A persistent storage key was empty.
    EmptyStorageKey,
    /// A persistent storage key contained unsupported characters.
    InvalidStorageKey,
    /// Storage schema version zero is reserved as invalid.
    InvalidStorageSchemaVersion,
    /// A migration did not move to a strictly newer schema.
    InvalidMigrationWindow,
    /// A retained reference hash name was empty.
    EmptyReferenceHashName,
    /// A retained reference hash name contained unsupported characters.
    InvalidReferenceHashName,
    /// The journal hash fact did not match the retained 14-bit mask.
    InvalidJournalHashFact,
    /// A storage or resource evidence class was not recognized.
    InvalidEvidenceClass,
    /// A fixture identity was empty.
    EmptyFixtureIdentity,
    /// A fixture identity contained path syntax.
    FixtureIdentityContainsPath,
    /// A fixture identity failed length or printable-character validation.
    InvalidFixtureIdentity,
    /// A resource runtime path was empty.
    EmptyResourcePath,
    /// A resource runtime path contained unsupported syntax or characters.
    InvalidResourcePath,
    /// A resource runtime path contained parent-directory traversal.
    ResourcePathContainsTraversal,
    /// A generated-output ownership value was not recognized.
    InvalidGeneratedOutputOwnership,
    /// A Bazel label was not in `//package:target` form.
    InvalidBazelLabel,
    /// A generated-output check label did not use the `_check` suffix.
    GeneratedCheckLabelMismatch,
    /// A generated-output update label did not use the `_update` suffix.
    GeneratedUpdateLabelMismatch,
    /// A Connect registration code was not in the expected user-visible shape.
    InvalidRegistrationCode,
    /// A Connect endpoint did not use an accepted URL scheme.
    InvalidConnectEndpoint,
    /// A GUI parity row ID was empty.
    EmptyGuiParityRowId,
    /// A GUI parity row ID contained unsupported syntax or characters.
    InvalidGuiParityRowId,
    /// A GUI display class was not recognized.
    InvalidDisplayClass,
    /// A GUI evidence class was not recognized.
    InvalidGuiEvidenceClass,
    /// A GUI proof scope was invalid for its evidence class.
    InvalidGuiProofScope,
    /// A GUI workflow was not recognized.
    InvalidGuiWorkflow,
    /// An intentional-delta status was not recognized.
    InvalidIntentionalDeltaStatus,
    /// A GUI semantic action was not recognized.
    InvalidGuiSemanticAction,
    /// A GUI semantic action was bound to the wrong workflow.
    InvalidGuiSemanticActionBinding,
    /// A network parity row ID was empty.
    EmptyNetworkParityRowId,
    /// A network parity row ID contained unsupported syntax or characters.
    InvalidNetworkParityRowId,
    /// A Phase 9 network evidence class was not recognized.
    InvalidNetworkEvidenceClass,
    /// A Phase 9 network proof scope was invalid for its evidence class.
    InvalidNetworkProofScope,
    /// A secret-handling value was not recognized.
    InvalidSecretHandling,
    /// A Connect command ID contained unsupported syntax or characters.
    InvalidConnectCommandId,
    /// A Connect command state was not recognized.
    InvalidConnectCommandState,
    /// A telemetry or event surface was not recognized.
    InvalidTelemetryEventSurface,
    /// A WebSocket command state was not recognized.
    InvalidWebSocketCommandState,
    /// A proxy mode was not recognized.
    InvalidProxyMode,
    /// A WUI endpoint family was not recognized.
    InvalidWuiEndpointFamily,
    /// A WUI auth mode was not recognized.
    InvalidWuiAuthMode,
    /// A transfer source was not recognized.
    InvalidTransferSource,
    /// A transfer slot state was not recognized.
    InvalidTransferSlotState,
    /// A transfer range end was before its start.
    InvalidTransferRange,
    /// Encrypted payload metadata attempted to carry invalid identity data.
    InvalidEncryptedPayloadMetadata,
    /// A transfer encryption mode was not recognized.
    InvalidTransferEncryptionMode,
    /// A transfer recovery state was not recognized.
    InvalidTransferRecoveryState,
    /// A transfer error class was not recognized.
    InvalidTransferErrorClass,
    /// A network service surface was not recognized.
    InvalidNetworkServiceSurface,
    /// A network service was requested without its required feature gate.
    UnsupportedNetworkService,
}

impl fmt::Display for InvariantError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::UnsupportedHardwareCombination {
                printer,
                board,
                mcu,
                bootloader_mode,
            } => write!(
                formatter,
                "unsupported firmware hardware combination: {printer:?}/{board:?}/{mcu:?}/{bootloader_mode:?}"
            ),
            Self::UnsupportedFeature {
                printer,
                board,
                feature,
            } => write!(
                formatter,
                "unsupported feature {feature:?} for firmware profile {printer:?}/{board:?}"
            ),
            Self::EmptyAuxiliaryParityRowId => {
                formatter.write_str("auxiliary parity row ID must not be empty")
            }
            Self::InvalidAuxiliaryParityRowId => formatter.write_str(
                "auxiliary parity row ID must be path-free printable ASCII at most 96 bytes",
            ),
            Self::InvalidAuxiliaryControllerKind => formatter.write_str(
                "auxiliary controller kind must be dwarf, modular-bed, xbuddy-extension, or mmu2",
            ),
            Self::InvalidAuxiliaryRuntimeState => formatter.write_str(
                "auxiliary runtime state must be one of the Phase 10 accepted values",
            ),
            Self::InvalidFirmwareImageSource => formatter.write_str(
                "firmware image source must be a named Phase 10 CMake variable or resource path",
            ),
            Self::InvalidAuxiliaryUpdateMode => formatter.write_str(
                "auxiliary update mode must be one of the Phase 10 accepted values",
            ),
            Self::InvalidModbusUnitIdentity => {
                formatter.write_str("Modbus unit identity must be in range 1..=247")
            }
            Self::InvalidModbusRequestKind => formatter
                .write_str("Modbus request kind must be one of the Phase 10 accepted values"),
            Self::InvalidBusEvidenceClass => formatter
                .write_str("bus evidence class must be one of the Phase 10 accepted values"),
            Self::InvalidAuxiliaryProofScope => formatter.write_str(
                "auxiliary proof scope must be local or non-local",
            ),
            Self::InvalidMmuTransportState => formatter
                .write_str("MMU transport state must be one of the Phase 10 accepted values"),
            Self::InvalidDockIdentity => formatter
                .write_str("dock identity must be MODULAR_BED, DWARF_1..DWARF_6, or XBUDDY_EXTENSION"),
            Self::InvalidToolOffsetIdentity => {
                formatter.write_str("tool offset identity tool number must be in range 1..=6")
            }
            Self::InvalidControllerFaultClass => formatter.write_str(
                "controller fault class must be one of the Phase 10 accepted values",
            ),
            Self::InvalidAuxiliaryParityContract => formatter.write_str(
                "auxiliary local proof scope cannot be paired with simulator, hardware, or manual evidence",
            ),
            Self::UnsupportedAuxiliaryController => formatter.write_str(
                "auxiliary controller requires a compatible validated product profile",
            ),
            Self::EmptyArtifactName => formatter.write_str("artifact name must not be empty"),
            Self::ArtifactNameContainsPath => {
                formatter.write_str("artifact name must not contain path syntax")
            }
            Self::ArtifactSuffixMismatch {
                kind,
                expected_suffix,
            } => write!(
                formatter,
                "artifact kind {kind:?} requires suffix {expected_suffix}"
            ),
            Self::EmptyStorageKey => formatter.write_str("storage key must not be empty"),
            Self::InvalidStorageKey => formatter.write_str(
                "storage key must contain only ASCII letters, digits, underscore, dash, or dot",
            ),
            Self::InvalidStorageSchemaVersion => {
                formatter.write_str("storage schema version must be greater than zero")
            }
            Self::InvalidMigrationWindow => {
                formatter.write_str("migration target schema must be newer than source schema")
            }
            Self::EmptyReferenceHashName => {
                formatter.write_str("reference hash name must not be empty")
            }
            Self::InvalidReferenceHashName => {
                formatter.write_str("reference hash name must be printable ASCII")
            }
            Self::InvalidJournalHashFact => {
                formatter.write_str("journal hash fact must use 14 mask bits and mask 0x3FFF")
            }
            Self::InvalidEvidenceClass => {
                formatter.write_str("evidence class must be one of the Phase 7 accepted values")
            }
            Self::EmptyFixtureIdentity => formatter.write_str("fixture identity must not be empty"),
            Self::FixtureIdentityContainsPath => {
                formatter.write_str("fixture identity must not contain path syntax")
            }
            Self::InvalidFixtureIdentity => {
                formatter.write_str("fixture identity must be printable ASCII and at most 96 bytes")
            }
            Self::EmptyResourcePath => formatter.write_str("resource path must not be empty"),
            Self::InvalidResourcePath => formatter.write_str(
                "resource path must not contain backslashes, control characters, or exceed 160 bytes",
            ),
            Self::ResourcePathContainsTraversal => {
                formatter.write_str("resource path must not contain parent-directory traversal")
            }
            Self::InvalidGeneratedOutputOwnership => formatter.write_str(
                "generated output ownership must be tracked-reviewed-source or generated-at-build",
            ),
            Self::InvalidBazelLabel => {
                formatter.write_str("Bazel label must use //package:target form")
            }
            Self::GeneratedCheckLabelMismatch => {
                formatter.write_str("generated check label must end with _check")
            }
            Self::GeneratedUpdateLabelMismatch => {
                formatter.write_str("generated update label must end with _update")
            }
            Self::InvalidRegistrationCode => formatter
                .write_str("registration code must contain eight ASCII alphanumeric characters"),
            Self::InvalidConnectEndpoint => {
                formatter.write_str("connect endpoint must start with http:// or https://")
            }
            Self::EmptyGuiParityRowId => formatter.write_str("GUI parity row ID must not be empty"),
            Self::InvalidGuiParityRowId => formatter.write_str(
                "GUI parity row ID must be a path-free kebab-case ASCII identifier at most 96 bytes",
            ),
            Self::InvalidDisplayClass => {
                formatter.write_str("display class must be 240x320, 480x320, or mock")
            }
            Self::InvalidGuiEvidenceClass => {
                formatter.write_str("GUI evidence class must be one of the Phase 8 accepted values")
            }
            Self::InvalidGuiProofScope => formatter.write_str(
                "GUI local proof scope cannot be paired with simulator, hardware, or manual evidence",
            ),
            Self::InvalidGuiWorkflow => {
                formatter.write_str("GUI workflow must be one of the Phase 8 accepted values")
            }
            Self::InvalidIntentionalDeltaStatus => {
                formatter.write_str("intentional delta status must be none, approved, or blocked")
            }
            Self::InvalidGuiSemanticAction => formatter.write_str(
                "GUI semantic action must be pause, resume, cancel, stop, reprint, or preview",
            ),
            Self::InvalidGuiSemanticActionBinding => formatter.write_str(
                "GUI semantic action must be bound to its required print workflow",
            ),
            Self::EmptyNetworkParityRowId => {
                formatter.write_str("network parity row ID must not be empty")
            }
            Self::InvalidNetworkParityRowId => formatter.write_str(
                "network parity row ID must be path-free printable ASCII at most 96 bytes",
            ),
            Self::InvalidNetworkEvidenceClass => formatter.write_str(
                "network evidence class must be one of the Phase 9 accepted values",
            ),
            Self::InvalidNetworkProofScope => formatter.write_str(
                "network local proof scope cannot be paired with simulator, hardware, or manual evidence",
            ),
            Self::InvalidSecretHandling => {
                formatter.write_str("secret handling must be none or named-only-redacted")
            }
            Self::InvalidConnectCommandId => formatter.write_str(
                "Connect command ID must be path-free printable ASCII at most 96 bytes",
            ),
            Self::InvalidConnectCommandState => formatter.write_str(
                "Connect command state must be one of the Phase 9 accepted values",
            ),
            Self::InvalidTelemetryEventSurface => formatter.write_str(
                "telemetry event surface must be one of the Phase 9 accepted values",
            ),
            Self::InvalidWebSocketCommandState => formatter.write_str(
                "WebSocket command state must be one of the Phase 9 accepted values",
            ),
            Self::InvalidProxyMode => {
                formatter.write_str("proxy mode must be disabled or http-connect-tls-only")
            }
            Self::InvalidWuiEndpointFamily => formatter
                .write_str("WUI endpoint family must be one of the Phase 9 accepted values"),
            Self::InvalidWuiAuthMode => {
                formatter.write_str("WUI auth mode must be one of the Phase 9 accepted values")
            }
            Self::InvalidTransferSource => {
                formatter.write_str("transfer source must be one of the Phase 9 accepted values")
            }
            Self::InvalidTransferSlotState => formatter
                .write_str("transfer slot state must be one of the Phase 9 accepted values"),
            Self::InvalidTransferRange => {
                formatter.write_str("transfer inclusive end must not be before start")
            }
            Self::InvalidEncryptedPayloadMetadata => formatter.write_str(
                "encrypted payload metadata must use a non-empty named identity without value bytes",
            ),
            Self::InvalidTransferEncryptionMode => formatter
                .write_str("transfer encryption mode must be none or aes-ctr"),
            Self::InvalidTransferRecoveryState => formatter
                .write_str("transfer recovery state must be one of the Phase 9 accepted values"),
            Self::InvalidTransferErrorClass => formatter
                .write_str("transfer error class must be one of the Phase 9 accepted values"),
            Self::InvalidNetworkServiceSurface => formatter
                .write_str("network service surface must be one of the Phase 9 accepted values"),
            Self::UnsupportedNetworkService => formatter.write_str(
                "network service requires Feature::Connect or Feature::WebUi to be enabled",
            ),
        }
    }
}

impl std::error::Error for InvariantError {}
