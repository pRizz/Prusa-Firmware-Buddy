#![forbid(unsafe_code)]

//! Pure firmware domain model for the Rust port.
//!
//! This crate is the functional core for early Rust firmware decisions. It
//! encodes product, board, storage, artifact, and protocol invariants before
//! adapter code can use unchecked primitive values.

pub mod artifact;
pub mod feature;
pub mod gui;
pub mod print;
pub mod product;
pub mod protocol;
pub mod resource;
pub mod safety;
pub mod storage;

pub use artifact::{ArtifactFileName, ArtifactKind, ArtifactRequest};
pub use feature::{
    BurstSteppingMode, Feature, FeatureSet, GateState, Phase6FeatureGate, Phase6FeatureGates,
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
        }
    }
}

impl std::error::Error for InvariantError {}
