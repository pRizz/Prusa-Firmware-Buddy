use crate::InvariantError;

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
}
