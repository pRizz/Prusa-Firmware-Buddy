use crate::InvariantError;

pub use crate::safety::EvidenceClass;

/// Persistent storage key parsed at the boundary before domain code uses it.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct StorageKey(String);

impl StorageKey {
    /// Parses a storage key using the conservative key character set expected
    /// by checked generated config surfaces.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(InvariantError::EmptyStorageKey);
        }

        if !raw.chars().all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '_' | '-' | '.')
        }) {
            return Err(InvariantError::InvalidStorageKey);
        }

        Ok(Self(raw))
    }

    /// Returns the storage key as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Non-zero persistent storage schema version.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct StorageSchemaVersion(u16);

impl StorageSchemaVersion {
    /// Creates a schema version. Version zero is invalid because it cannot
    /// distinguish an initialized schema from a sentinel default.
    pub fn new(raw: u16) -> Result<Self, InvariantError> {
        if raw == 0 {
            return Err(InvariantError::InvalidStorageSchemaVersion);
        }

        Ok(Self(raw))
    }

    /// Returns the raw schema version.
    pub fn get(self) -> u16 {
        self.0
    }
}

/// Migration edge between two persistent storage schema versions.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MigrationWindow {
    from: StorageSchemaVersion,
    to: StorageSchemaVersion,
}

impl MigrationWindow {
    /// Creates a migration only when it moves to a newer schema version.
    pub fn new(
        from: StorageSchemaVersion,
        to: StorageSchemaVersion,
    ) -> Result<Self, InvariantError> {
        if to <= from {
            return Err(InvariantError::InvalidMigrationWindow);
        }

        Ok(Self { from, to })
    }

    /// Returns the source schema version.
    pub fn from(self) -> StorageSchemaVersion {
        self.from
    }

    /// Returns the target schema version.
    pub fn to(self) -> StorageSchemaVersion {
        self.to
    }
}

/// Raw persistent-store hash name from the reference firmware source.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ReferenceHashName(String);

impl ReferenceHashName {
    /// Parses a non-empty printable ASCII hash name exactly as the retained
    /// `journal::hash("...")` source records it.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(InvariantError::EmptyReferenceHashName);
        }

        if !raw.bytes().all(|byte| (0x20..=0x7e).contains(&byte)) {
            return Err(InvariantError::InvalidReferenceHashName);
        }

        Ok(Self(raw))
    }

    /// Returns the raw reference hash name as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Journal hash-space fact preserved from the reference generator.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct JournalHashFact {
    mask_bits: u8,
    mask: u16,
}

impl JournalHashFact {
    /// Creates the Phase 7 journal hash fact. The reference generator masks the
    /// first SHA-256 half-bytes with `0x3FFF`, giving a 14-bit identity space.
    pub fn new(mask_bits: u8, mask: u16) -> Result<Self, InvariantError> {
        if mask_bits != 14 || mask != 0x3FFF {
            return Err(InvariantError::InvalidJournalHashFact);
        }

        Ok(Self { mask_bits, mask })
    }

    /// Returns the number of retained hash-space mask bits.
    pub fn mask_bits(self) -> u8 {
        self.mask_bits
    }

    /// Returns the retained hash-space mask.
    pub fn mask(self) -> u16 {
        self.mask
    }
}

/// Phase 7 policy for credential-bearing storage evidence.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum CredentialRedactionPolicy {
    /// Only the credential-bearing reference name may appear in evidence.
    NameOnlyRedacted,
}

impl CredentialRedactionPolicy {
    /// Returns whether the policy permits credential value material.
    pub fn allows_value_material(self) -> bool {
        match self {
            Self::NameOnlyRedacted => false,
        }
    }
}

impl EvidenceClass {
    /// Parses a Phase 7 evidence class string.
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
            _ => Err(InvariantError::InvalidEvidenceClass),
        }
    }
}

/// Named storage, filesystem, and retained-storage-driver compatibility surface.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum FilesystemSurface {
    /// Removable USB media exposed through FatFs.
    UsbFatFs,
    /// Internal flash exposed through littlefs.
    InternalLittleFs,
    /// BBF/resource image exposed through littlefs.
    BbfLittleFs,
    /// Optional semihosting filesystem.
    Semihosting,
    /// Root listing over registered devices.
    RootListing,
    /// POSIX-like libsysbase devoptab dispatch.
    LibsysbaseDevoptab,
    /// EEPROM/internal flash persistent storage driver.
    EepromStorageDriver,
}

impl FilesystemSurface {
    /// Returns the runtime path or identity string for the surface.
    pub fn runtime_path(self) -> &'static str {
        match self {
            Self::UsbFatFs => "/usb",
            Self::InternalLittleFs => "/internal",
            Self::BbfLittleFs => "/bbf",
            Self::Semihosting => "/semihosting",
            Self::RootListing => "/",
            Self::LibsysbaseDevoptab => "POSIX-like devoptab",
            Self::EepromStorageDriver => "EEPROM/internal flash",
        }
    }
}

/// Storage compatibility identity represented by a Phase 7 contract row.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum StorageCompatibilityIdentity {
    /// Reference persistent-store hash name.
    ReferenceHashName(ReferenceHashName),
    /// Retained filesystem or storage-driver surface.
    FilesystemSurface(FilesystemSurface),
}

/// Source-backed Phase 7 storage compatibility claim.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StorageCompatibilitySurface {
    identity: StorageCompatibilityIdentity,
    evidence_class: EvidenceClass,
    maybe_credential_redaction_policy: Option<CredentialRedactionPolicy>,
}

impl StorageCompatibilitySurface {
    /// Creates a non-credential reference hash-name compatibility surface.
    pub fn reference_hash_name(
        reference_hash_name: ReferenceHashName,
        evidence_class: EvidenceClass,
    ) -> Self {
        Self {
            identity: StorageCompatibilityIdentity::ReferenceHashName(reference_hash_name),
            evidence_class,
            maybe_credential_redaction_policy: None,
        }
    }

    /// Creates a credential-bearing reference hash-name surface with name-only
    /// redaction. There is no field that can hold credential value material.
    pub fn credential_reference_hash_name(
        reference_hash_name: ReferenceHashName,
        evidence_class: EvidenceClass,
    ) -> Self {
        Self {
            identity: StorageCompatibilityIdentity::ReferenceHashName(reference_hash_name),
            evidence_class,
            maybe_credential_redaction_policy: Some(CredentialRedactionPolicy::NameOnlyRedacted),
        }
    }

    /// Creates a filesystem or storage-driver compatibility surface.
    pub fn filesystem_surface(
        filesystem_surface: FilesystemSurface,
        evidence_class: EvidenceClass,
    ) -> Self {
        Self {
            identity: StorageCompatibilityIdentity::FilesystemSurface(filesystem_surface),
            evidence_class,
            maybe_credential_redaction_policy: None,
        }
    }

    /// Returns the compatibility identity.
    pub fn identity(&self) -> &StorageCompatibilityIdentity {
        &self.identity
    }

    /// Returns the evidence class.
    pub fn evidence_class(&self) -> EvidenceClass {
        self.evidence_class
    }

    /// Returns the credential redaction policy when this is a credential row.
    pub fn credential_redaction_policy(&self) -> Option<CredentialRedactionPolicy> {
        self.maybe_credential_redaction_policy
    }

    /// Returns whether this row permits credential value material.
    pub fn allows_value_material(&self) -> bool {
        self.maybe_credential_redaction_policy
            .is_some_and(CredentialRedactionPolicy::allows_value_material)
    }
}

/// Synthetic fixture identity for storage and migration evidence.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct FixtureIdentity(String);

impl FixtureIdentity {
    /// Parses a fixture identity that cannot escape into filesystem path syntax.
    pub fn parse(raw: impl Into<String>) -> Result<Self, InvariantError> {
        let raw = raw.into();
        if raw.is_empty() {
            return Err(InvariantError::EmptyFixtureIdentity);
        }

        if raw.len() > 96 || raw.bytes().any(|byte| byte.is_ascii_control()) {
            return Err(InvariantError::InvalidFixtureIdentity);
        }

        if raw == ".." || raw.contains('/') || raw.contains('\\') {
            return Err(InvariantError::FixtureIdentityContainsPath);
        }

        Ok(Self(raw))
    }

    /// Returns the fixture identity as a string slice.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_zero_schema_version() {
        // Arrange
        let raw_version = 0;

        // Act
        let result = StorageSchemaVersion::new(raw_version);

        // Assert
        assert_eq!(result, Err(InvariantError::InvalidStorageSchemaVersion));
    }

    #[test]
    fn rejects_reverse_migration_window() {
        // Arrange
        let from = StorageSchemaVersion::new(4).expect("non-zero schema version is valid");
        let to = StorageSchemaVersion::new(3).expect("non-zero schema version is valid");

        // Act
        let result = MigrationWindow::new(from, to);

        // Assert
        assert_eq!(result, Err(InvariantError::InvalidMigrationWindow));
    }

    #[test]
    fn accepts_forward_migration_window() {
        // Arrange
        let from = StorageSchemaVersion::new(1).expect("non-zero schema version is valid");
        let to = StorageSchemaVersion::new(2).expect("non-zero schema version is valid");

        // Act
        let result = MigrationWindow::new(from, to);

        // Assert
        assert!(matches!(result, Ok(window) if window.from() == from && window.to() == to));
    }

    #[test]
    fn rejects_storage_key_with_whitespace() {
        // Arrange
        let raw_key = "network ssid";

        // Act
        let result = StorageKey::parse(raw_key);

        // Assert
        assert_eq!(result, Err(InvariantError::InvalidStorageKey));
    }

    #[test]
    fn accepts_raw_reference_hash_name_with_spaces() {
        // Arrange
        let raw_name = "WIFI AP Password";

        // Act
        let storage_key_result = StorageKey::parse(raw_name);
        let reference_hash_result = ReferenceHashName::parse(raw_name);

        // Assert
        assert_eq!(storage_key_result, Err(InvariantError::InvalidStorageKey));
        assert!(matches!(
            reference_hash_result,
            Ok(name) if name.as_str() == raw_name
        ));
    }

    #[test]
    fn rejects_empty_reference_hash_name() {
        // Arrange
        let raw_name = "";

        // Act
        let result = ReferenceHashName::parse(raw_name);

        // Assert
        assert_eq!(result, Err(InvariantError::EmptyReferenceHashName));
    }

    #[test]
    fn validates_journal_hash_fact_mask() {
        // Arrange
        let expected_mask_bits = 14;
        let expected_mask = 0x3FFF;

        // Act
        let valid_result = JournalHashFact::new(expected_mask_bits, expected_mask);
        let invalid_result = JournalHashFact::new(13, 0x1FFF);

        // Assert
        assert!(valid_result.is_ok());
        assert_eq!(invalid_result, Err(InvariantError::InvalidJournalHashFact));
    }

    #[test]
    fn name_only_credential_redaction_rejects_value_material() {
        // Arrange
        let policy = CredentialRedactionPolicy::NameOnlyRedacted;

        // Act
        let allows_value_material = policy.allows_value_material();

        // Assert
        assert!(!allows_value_material);
    }

    #[test]
    fn maps_filesystem_surfaces_to_runtime_paths() {
        // Arrange
        let cases = [
            (FilesystemSurface::UsbFatFs, "/usb"),
            (FilesystemSurface::InternalLittleFs, "/internal"),
            (FilesystemSurface::BbfLittleFs, "/bbf"),
            (FilesystemSurface::Semihosting, "/semihosting"),
            (FilesystemSurface::RootListing, "/"),
            (FilesystemSurface::LibsysbaseDevoptab, "POSIX-like devoptab"),
            (
                FilesystemSurface::EepromStorageDriver,
                "EEPROM/internal flash",
            ),
        ];

        // Act / Assert
        for (surface, expected_path) in cases {
            assert_eq!(surface.runtime_path(), expected_path);
        }
    }

    #[test]
    fn parses_valid_evidence_class() {
        // Arrange
        let raw_class = "manual-hardware-required";

        // Act
        let result = EvidenceClass::parse(raw_class);

        // Assert
        assert!(matches!(result, Ok(EvidenceClass::ManualHardwareRequired)));
    }

    #[test]
    fn rejects_invalid_evidence_class_phrase() {
        // Arrange
        let raw_class = "hardware verified locally";

        // Act
        let result = EvidenceClass::parse(raw_class);

        // Assert
        assert_eq!(result, Err(InvariantError::InvalidEvidenceClass));
    }

    #[test]
    fn rejects_fixture_identity_with_path_syntax() {
        // Arrange
        let raw_identity = "../secret.bin";

        // Act
        let result = FixtureIdentity::parse(raw_identity);

        // Assert
        assert_eq!(result, Err(InvariantError::FixtureIdentityContainsPath));
    }

    #[test]
    fn rejects_fixture_identity_parent_segment() {
        // Arrange
        let raw_identity = "..";

        // Act
        let result = FixtureIdentity::parse(raw_identity);

        // Assert
        assert_eq!(result, Err(InvariantError::FixtureIdentityContainsPath));
    }

    #[test]
    fn rejects_oversized_fixture_identity() {
        // Arrange
        let raw_identity = "a".repeat(97);

        // Act
        let result = FixtureIdentity::parse(raw_identity);

        // Assert
        assert_eq!(result, Err(InvariantError::InvalidFixtureIdentity));
    }

    #[test]
    fn credential_storage_surface_keeps_value_material_disallowed() {
        // Arrange
        let reference_hash_name =
            ReferenceHashName::parse("Connect Token").expect("reference name is valid");

        // Act
        let surface = StorageCompatibilitySurface::credential_reference_hash_name(
            reference_hash_name,
            EvidenceClass::SourceAudit,
        );

        // Assert
        assert_eq!(
            surface.credential_redaction_policy(),
            Some(CredentialRedactionPolicy::NameOnlyRedacted)
        );
        assert!(!surface.allows_value_material());
    }
}
