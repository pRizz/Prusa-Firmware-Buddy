#![forbid(unsafe_code)]

//! Pure firmware domain model for the Rust port.
//!
//! This crate is the functional core for early Rust firmware decisions. It
//! encodes product, board, storage, artifact, and protocol invariants before
//! adapter code can use unchecked primitive values.

pub mod artifact;
pub mod feature;
pub mod print;
pub mod product;
pub mod protocol;
pub mod safety;
pub mod storage;

pub use artifact::{ArtifactFileName, ArtifactKind, ArtifactRequest};
pub use feature::{Feature, FeatureSet};
pub use print::{
    CommandRoute, FixtureId, GcodeMnemonic, PlannerFlowState, PrintCommand, PrintJobState,
    PrintSource, PrintTransitionError, route_gcode_mnemonic, transition_print_state,
};
pub use product::{BoardKind, BootloaderMode, McuKind, PrinterKind, ProductProfile};
pub use protocol::{ConnectEndpoint, Connected, Disconnected, Registered, RegistrationCode};
pub use safety::{
    EvidenceClass, FatalPathPolicy, SafetyAction, SafetyFlow, SafetyPolicySurface,
    classify_safety_flow,
};
pub use storage::{MigrationWindow, StorageKey, StorageSchemaVersion};

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
    /// A Connect registration code was not in the expected user-visible shape.
    InvalidRegistrationCode,
    /// A Connect endpoint did not use an accepted URL scheme.
    InvalidConnectEndpoint,
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
            Self::InvalidRegistrationCode => formatter
                .write_str("registration code must contain eight ASCII alphanumeric characters"),
            Self::InvalidConnectEndpoint => {
                formatter.write_str("connect endpoint must start with http:// or https://")
            }
        }
    }
}

impl std::error::Error for InvariantError {}
